'''Represents a single rendering node.'''

import os.path
import random
import threading
import StringIO
import time

# Work around deprecation since Python 2.6
try: from hashlib import md5
except ImportError: from md5 import md5


from multiblend.popen import DebuggingPopen
from multiblend.logging import Logger

def non_existing_file(path, __lock__=threading.Lock()):
    '''Returns a filename which is ensured not to exist (yet) in the
    path.

    >>> a = non_existing_file('/tmp')
    >>> os.path.exists(a)
    False
    >>> file(a, 'w').close()
    >>> os.path.exists(a)
    True
    >>> b = non_existing_file('/tmp')
    >>> os.path.exists(b)
    False
    >>> a != b
    True
    >>> os.unlink(a)

    '''

    __lock__.acquire()

    try:
        digest = md5('somefile')
        for count in xrange(1000):
            filename = os.path.join(path, digest.hexdigest())
            if not os.path.exists(filename):
                return filename

            random.jumpahead(count)
            letter = random.choice('abcdefghijklmnopqrstuvwxyz')
            digest.update(letter)
    finally:
        __lock__.release()
    
    raise RuntimeError('Could not find non-existing name')

class Node(object):
    '''Representation of a node.'''

    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.hostname = config[name]['hostname']
        self.blender = config[name]['blender']
        self.workdir = config[name]['workdir']
        self.echoing_shell = config[name]['echoing_shell']
        self.outputpath = config['outputpath']
        self.log = Logger(self.hostname)

        self.shell = None
        self.rendering = False
        self.blenderpid = None
    
    def needs_connection(func):
        '''Function decorator.

        Ensures there is a connected shell before the decorated
        function is called.
        '''

        def connect_and_call(self, *args, **kwargs):
            '''Connects if self.shell is None, then calls the
            decorated funcion.
            '''
            if self.shell is None:
                self.log.debug('Implicitly connecting to call %s' % func)
                self.connect()

            return func(self, *args, **kwargs)

        return connect_and_call
        
    def connect(self):
        '''Connects to this node.

        Sets self.shell to the connected shell. Use self.send() and
        self.readline() to communicate with host.

        Returns self.shell.
        '''

        self.shell = self.create_connection()
        if not self.shell:
            self.log.critical('Unable to create shell!')
            raise RuntimeError('Unable to create shell!')

        self.send_blenderstarter()

        return self.shell

    def __del__(self):
        '''Cleans up the node'''

        self.log.debug('Cleaning up')

        if not self.shell:
            # No connection was made, so nothing to clean up
            return

        try:
                self.remove_blenderstarter()
        except:
            self.log.exception('Error while removing blenderstarter')

        try:
            self.disconnect()
        except:
            self.log.exception('Error while disconnecting')

    def create_connection(self):
        '''Connects to this node.

        Returns a DebuggingPopen object connected to the shell.
        '''

        cmd = '%s %s sh' % (self.config['ssh'], self.hostname)

        self.log.debug('Starting "%s"' % cmd)
        shell = DebuggingPopen(self.log, cmd)
        if not shell:
            self.log.critical('Unable to create shell!')
            raise RuntimeError('Unable to create shell!')

        if self.echoing_shell:
            shell.send('stty -echo')
            shell.readline()
        shell.send('export TERM=vt100')

        return shell

    def disconnect(self):
        '''Disconnects this node.
        
        Returns the exit status. See DebuggingOpen.wait()
        '''

        if self.shell is None: return

        status = self.disconnect_connection(self.shell)
        self.shell = None

        return status
    
    def disconnect_connection(self, shell):
        '''Disconnects the shell.

        Returns the exit status. See DebuggingOpen.wait()
        '''

        shell.send('exit')
        shell.stdin.close()
        shell.stdout.close()

        return shell.wait()

    @needs_connection
    def send(self, line):
        '''Sends 'line' to the shell'''
        return self.shell.send(line)

    @needs_connection
    def readline(self):
        '''Returns a line from the shell'''

        return self.shell.readline()

    @needs_connection
    def test_blender_executable(self):
        '''Tests the existance and executable-ness of blender.'''

        blender = self.blender
        self.send('[ -x %s ] && echo TRUE || echo FALSE' % blender)
        
        if self.readline().strip() == 'TRUE':
            return True

        self.log.error('Blender %s is not executable on node %s' % (blender,
            self.name))
        return False

    def test(self):
        '''Tests this node.

        Returns True if the node is okay, returns False otherwise.
        '''

        # No longer an issue, since we no longer use NFS
        #if not self.test_create_file():
        #   return False

        try:
            if not self.test_blender_executable():
                return False
        except Exception, e:
            self.log.info('Test failed: %s' % e)
            return False

        self.log.debug('Host %s okay' % self.hostname)

        return True

    def __str__(self):
        return '[%s %s]' % (self.name, self.hostname)
    
    def __unicode__(self):
        return unicode(str(self))

    def blend(self, blenderfile, start, end):
        '''Runs blender on the node.

        Renders the file 'blenderfile; from frame 'start' to frame
        'end'. Does this in its own thread, returning when the blender
        job is done.

        The frames are copied to the master node using scp.
        '''

        self.send_blenderstarter()

        blenderstarter = os.path.join(self.workdir, 'blenderstarter')
        
        remotefile = os.path.join(self.workdir, blenderfile)
        self.send_file(file(blenderfile), remotefile)
        blenderfile = remotefile

        self.send('"%s" "%s" "%s" %i %i'
                % (blenderstarter, self.blender, blenderfile, start, end))

        self.blenderpid = int(self.readline().strip())

        line = None
        while line != 'DONE':
            line = self.readline().strip()
            
            # Skip empty lines and lines with \r in them - those
            # contain progress information which is annoying on a
            # multi-node system.
            if line and '\r' not in line:
                self.log.debug(line)

            # Handle saved frames. Those are reported as
            # Saved: /tmp/0001.jpg Time: 00:00.70
            if line.startswith('Saved: '):
                try:
                    self.fetch_saved_file(line.split()[1])
                except RuntimeError, e:
                    self.log.error('Aborted due to RuntimeError: %s' % e)
                    self.rendering = False
                    raise

        self.blenderpid = None

    def renderchunks(self, blenderfile, dispatcher):
        '''Renders chunks from the dispatcher in a separate thread.

        The dispatcher is queried for chunks of frames, and they are
        rendered. If no more frames are available, the thread stops.

        This function returns immediately after starting the new
        thread.

        Returns the thread object.
        '''

        def thread():
            '''The thread that actually does the rendering.'''

            self.rendering = True

            while self.rendering:

                # Get another chunk of frames
                chunk = dispatcher.chunk()
                if chunk is None:
                    self.rendering = False
                    break

                # Render the frames
                self.log.info('rendering %s' % (chunk, ))
                (start, end) = chunk

                start_time = time.time()
                self.blend(blenderfile, start, end)
                if time.time() - start_time < 2:
                    self.log.error('Rendering takes too little time, '
                    'something must be wrong. Aborted this node.')
                    self.rendering = False

            self.log.info("I'm done, no more chunks left for me.")

        renderthread = threading.Thread(target=thread)
        renderthread.setDaemon(True)
        renderthread.start()

        return renderthread

    def abort(self):
        '''Tries to abort this node.
        
        Creates a new SSH connection to the node, and kills the
        blender instance. It won't touch other blender instances
        running on the same host.
        '''

        self.rendering = False

        if self.blenderpid:
            killshell = self.create_connection()
            killshell.send('kill %i' % self.blenderpid)
    
    def fetch_saved_file(self, filename):
        '''Fetches the remote file 'filename' from the node, and
        stores it in the local output directory.

        'filename' should be the filename on the node. It will be
        stored in the outputpath configured in the [main] section of
        the config file.
        '''

        # Build the scp command
        outputpath = self.outputpath
        cmd = '%s %s:%s %s' % (self.config['scp'], self.hostname, filename, outputpath)
        self.log.debug('Running %s' % cmd)

        # Copy the frame
        result = os.system(cmd)

        # Check result of command. Do it thoroughly, because failure
        # to fetch the images defeats the entire rendering process.
        if os.WCOREDUMP(result):
            msg = 'Coredump while fetching %s' % filename
            self.log.critical(msg)
            raise RuntimeError(msg)
        
        if not os.WIFEXITED(result):
            msg = 'scp process did not finish properly while ' \
                    'fetching %s' % filename
            self.log.critical(msg)
            raise RuntimeError(msg)

        status = os.WEXITSTATUS(result)
        if status > 0:
            msg = 'scp process exited with error status %i while ' \
                    'fetching %s' % (status, filename)
            self.log.critical(msg)
            raise RuntimeError(msg)
    
        self.log.info('Saved %s' % filename)
    
    @needs_connection
    def send_blenderstarter(self):
        '''Sends the blenderstarter script to the client.

        The script starts blender in the background, reports the PID of
        blender so that we can kill it if required, then waits for Blender
        to finish. After that, DONE is echoed so we know it's done.
        '''

        starter = '''\
        #!/bin/sh

        if [ -z "$4" ]; then
            echo "Usage: $0 <blender> <blenderfile> <start> <end>"
            exit 1
        fi

        nice -n %(nice)i $1 -b "$2" -s $3 -e $4 -a %(scene)s 2>&1 &
        BLENDERPID=$!

        echo $BLENDERPID
        wait $BLENDERPID
        echo DONE
        '''.replace(8 * ' ', '')

        # Set scene name option if a scene was passed
        if self.config['scene']:
            scene = '-S %s' % self.config['scene']
        else:
            scene = ''

        starter = starter % {
                'nice': self.config['nice'],
                'scene': scene
            }

        path = os.path.join(self.workdir, 'blenderstarter')
        self.send_file(StringIO.StringIO(starter), path)
        self.send('chmod +x %s' % path)

    @needs_connection
    def send_file(self, fileobj, remotename):
        '''Sends the contents of file-like object 'fileobj' to the
        node, saving it as 'remotename'.
        '''
        
        tmpfilename = non_existing_file('/tmp')
        tmpfile = open(tmpfilename, 'w')
        tmpfile.write(fileobj.read())
        tmpfile.close()

        cmd = '%s %s %s:%s' % (self.config['scp'], tmpfilename, self.hostname, remotename)
        self.log.debug('Running %s' % cmd)

        # Copy the file
        result = os.system(cmd)

        # Check result of command. Do it thoroughly, because failure
        # to fetch the images defeats the entire rendering process.
        if os.WCOREDUMP(result):
            msg = 'Coredump while sending %s' % remotename
            self.log.critical(msg)
            raise RuntimeError(msg)
        
        if not os.WIFEXITED(result):
            msg = 'scp process did not finish properly while ' \
                    'sending %s' % remotename
            self.log.critical(msg)
            raise RuntimeError(msg)

        status = os.WEXITSTATUS(result)
        if status > 0:
            msg = 'scp process exited with error status %i while ' \
                    'sending %s' % (status, remotename)
            self.log.critical(msg)
            raise RuntimeError(msg)
    
        try:
            os.remove(tmpfilename)
        except IOError, e:
            self.log.warn('Unable to remove temporary file %s: %s' %
                    (tmpfilename, e))

    @needs_connection
    def remove_blenderstarter(self):
        '''Removes the blender starter script.'''

        blenderstarter = os.path.join(self.workdir, 'blenderstarter')
        self.send('rm -f %s' % blenderstarter)

