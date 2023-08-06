#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Multiblend - simple distributed Blender rendering.

Usage:
    multiblend.py \\
            -b <blenderfile> \\
            -s <startframe> \\
            -e <endframe> \\
            [-T] \\
            [-S Scene name] \\
            [-E]

    The -T option will cause Multiblend to skip testing the nodes.
    The -S option can denote the scene to render.
    The -E option will cause Multiblend to skip frames that already exist.

Configuration
=============

Configuration is read from /etc/multiblend and ~/.multiblendrc. Below
you find an example config file::

    [main]
    chunks=100
    nodes=2
    outputpath=/home/sybren/documents/blender/output
    ssh=/usr/bin/ssh -Tq
    scp=/usr/bin/scp -q
    echoing_shell=False
    nice=3

    [node0]
    hostname=localhost
    blender=/home/sybren/blender-2.41-linux-glibc232-py24-i386/blender
    workdir=/home/sybren/tmp

    [node1]
    hostname=zebra
    blender=/home/sybren/blender-2.41-linux-glibc232-py24-i386/blender
    workdir=/tmp

The list of nodes should contain the hostnames or IP addresses of the
nodes, the path to the Blender executable, and the working directory.
The number of nodes should be set in the [main] section.

The 'echoing_shell' option is optional and defaults to False. It can
be set in the [main] section for all the nodes, and can be specified
for specific nodes. First try without this option. If you get the
message that Blender is not executable on nodes where it actually is
executable, try echoing_shell=True.

WARNING: The working directory should be different from the directory
the blender file is in. Otherwise, you might lose your work.

Setting up a node
=================

The node where this script is run, is called the "master node". All
other nodes are just called "node".

The node should be reachable from the master node using SSH, without
having to type a password. Use 'ssh-keygen' to generate a suitable SSH
key, and use 'ssh-copy-id' to copy the key from the master node to the
other nodes. That generally does the trick. If you want to run a
Blender instance on the master node as well, include a node with
hostname=localhost.

License
=======

This software is covered by the Gnu Public License, or GPL. For more
information, see http://www.stuvel.eu/license.
'''

# Changes:
#
# 2006-05-01, version 1.0
#  - Initial version/home/sstuvel/sadako/presentaties/20060520:
#
# 2006-05-01, version 1.1
#  - The used chunk size is the maximum of the configured chunk size,
#    and the number of frames to render divided by the number of
#    nodes. This tries to ensure all nodes are used, even for a small
#    number of rendered frames.
#  - Logging prints node hostname instead of number.
#  - Pressing Ctrl+C properly stops Blender on all nodes.
#
# 2006-05-10, version 1.2
#  - No longer need NFS, files are copied via scp instead. This does
#    add the requirement that all external files (fonts, textures,
#    etc.) either should be already available on the nodes, or be
#    packed inside the Blender file.
#  - Removed the special hostname LOCAL. In its stead, just use
#    hostname=localhost. This made the code more stable and clean.
#
# 2005-05-29, version 1.3
#  - Start 'sh' immediately on the node. This prevents 'last logged in
#    on ...' messages upon login.
#  - Added echoing_node to the config possibilities.
#  - Added nice level to the config possibilities.
#  - Added possibility to skip node testing.
#  - Fixed chunk size bug when nr of nodes is larger than nr of frames
#    to render.
#  - Fixed encoding bug when stdout is not a terminal.
#  - Added possibility to select the scene to render.
#
# in development, version 1.4
#  - Display timing info after rendering.
#  - Added -E option to skip existing frames.
#  - Smarter distribution of frames
#
# Ideas for future versions:
#  - Perform check on all nodes, output multiblendrc file with only
#    those nodes that passed the checks.
#  - Display list of missing frames, optionally rendering only those.

__author__ = 'Sybren A. Stüvel'
__email__ = 'sybren@stuvel.eu'
__revision__ = '1.4-beta0'
__url__ = 'http://www.stuvel.eu/multiblend'

import ConfigParser
import datetime
import getopt
import glob
import logging
import md5
import os
import os.path
import popen2
import random
import StringIO
import sys
import threading
import time

logging.basicConfig()
log = logging.getLogger('multiblend')
log.setLevel('DEBUG' in os.environ and logging.DEBUG or logging.INFO)

node_loglevel = logging.INFO

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
        self.log = logging.getLogger(self.hostname)
        self.log.setLevel(node_loglevel)

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

        Returns a popen2.Popen3 object connected to the shell.
        '''

        cmd = '%s %s sh' % (config['ssh'], self.hostname)

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
        shell.tochild.close()
        shell.fromchild.close()

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

class DebuggingPopen(popen2.Popen3):
    '''Popen4 class, augmented for debugging and easier I/O. Easier
    for this project, anyway ;-)
    '''

    def __init__(self, log, *args, **kwargs):
        self.log = log
        popen2.Popen3.__init__(self, *args, **kwargs)

    def send(self, line):
        '''Sends a line of text to the process.

        A newline is appended for your convenience.
        '''

        self.log.debug('Sending: %s' % line)
        print >> self.tochild, line
        self.tochild.flush()
    
    def readline(self):
        '''Returns a line of text from the client.'''

        line = self.fromchild.readline()
        stripped = line.strip()
        if stripped:
            self.log.debug('Received: %s' % stripped)

        return line

class FrameDispatcher(object):
    '''Frame dispatcher for render nodes.

    The dispatcher is initialized with a starting and ending frame
    number, and the size of the chunks dispatched. Every rendering
    thread can then ask for a new chunk of frames to render. When no
    more frames are available, None is returned.

    This dispatching is done in a thread-safe fashion. Threads can
    thus simply call chunk() without having to mess with locks etc.

    >>> fd = FrameDispatcher(1, 201, 100)
    >>> fd.chunk()
    (1, 100)
    >>> fd.chunk()
    (101, 200)
    >>> fd.chunk()
    (201, 201)
    >>> fd.chunk()
    None
    '''

    def __init__(self, start, end, chunksize, output_path=None):
        '''Constructor, see class docstring for usage.'''
        
        self.start = start
        self.end = end
        self.chunksize = chunksize

        if chunksize < 1:
            raise ValueError('Chunk size should be > 0')
        if start > end:
            raise ValueError('Start should be before end')

        # Figure out the ranges we have to render
        if output_path:
            self.ranges = self._find_ranges(start, end, output_path)
        else:
            self.ranges = [(start, end)]

        log.debug('Created new %s %i -> %i, %i-size chunks' %
                (self.__class__, start, end, chunksize))

        self.lock = threading.RLock()

    def __str__(self):
        return '[%s %i -> %i, %i-size chunks]' % \
                (self.__class__, self.start, self.end, self.chunksize)

    def __unicode__(self):
        return unicode(str(self))

    def _find_ranges(self, start, end, output_path):
        '''Returns a list of ranges [(r_start, r_end), ...] of non-existing
        frames in the output path.
        '''

        log.info('Finding missing frames on %s' % output_path)

        def framenr(filename):
            basename = os.path.basename(filename)
            (frame, ext) = os.path.splitext(basename)
            try:
                return int(frame, 10)
            except ValueError:
                return None

        # Start by getting a list of rendered frames.
        files = glob.glob(os.path.join(output_path, '[0-9]*'))
        rendered = set()
        for f in files:
            nr = framenr(f)
            if nr is not None: rendered.add(nr)
        log.debug('Rendered frames: %s' % rendered)

        # Examine the frame numbers to find holes.
        allframes = set(range(start, end+1))
        missing = sorted(list(allframes - rendered))
        log.debug('Missing frames: %s' % missing)

        # Now group the missing frames into ranges
        ranges = []
        start = None
        total_missing = len(missing)
        for index, thisframe in enumerate(missing):
            # This frame is the start if we're not in a range already
            if start is None:
                start = thisframe
                log.debug('Start of missing range: %i' % start)
            
            # This frame is the end if this is the last frame, or the next frame
            # is more than one frame away
            if index == total_missing - 1 or missing[index+1] > thisframe+1:
                end = thisframe
                log.debug('End of missing range: %i' % end)
                ranges.append((start, end))

                # Start over with a new range
                start = None

        log.info('Missing frames: %s' % ', '.join(['%s-%s' % r for r in ranges]))
        return ranges

    def chunk(self):
        '''Returns a new chunk of frames.

        Returns a tuple (start, end) or None if there are no more
        frames to dispatch.
        '''

        self.lock.acquire()

        # Maybe we're already out of frames.
        if not self.ranges:
            self.lock.release()
            return None
        
        # Get a new range to render
        start, end = self.ranges.pop(0)
        
        # If the range is larger than the maximum chunk size, we can't use the
        # entire range and have to split it up
        if end - start + 1 > self.chunksize:
            new_start = start + self.chunksize

            # Put a new range back
            self.ranges.insert(0, (new_start, end))
            end = new_start - 1

        self.lock.release()

        log.debug('Ranges left: %s' % self.ranges)

        return (start, end)

    def reset(self):
        '''Resets the FrameDispatcher.

        Subsequent calls to chunk() will return the same values as
        when the FrameDispatcher was just created.
        '''

        self.lock.acquire()
        self.next_chunk = self.start
        self.lock.release()

def node_names(config):
    '''Generator, iterates over the node names'''

    for nodenr in xrange(config['nodes']):
        yield 'node%i' % nodenr

def load_config():
    '''Loads the configuration file.
    
    Loads the config from /etc/multiblend and ~/.multiblendrc.
    '''

    conf = ConfigParser.ConfigParser()
    home = os.environ['HOME']
    read = conf.read(['/etc/multiblend', '%s/.multiblendrc' % home])
    if not read:
        print __doc__
        raise SystemExit('No configuration file found. An example '
                'file can be seen above, in the documentation. Place '
                'it in ~/.multiblendrc and alter it to match your '
                'situation.')

    # Read the main config
    try:
        config = dict(
                outputpath=conf.get('main', 'outputpath'),
                chunks=conf.getint('main', 'chunks'),
                nodes=conf.getint('main', 'nodes'),
                ssh=conf.get('main', 'ssh'),
                scp=conf.get('main', 'scp'),
                nice=conf.getint('main', 'nice'),
            )
    except ConfigParser.NoOptionError, e:
        print __doc__
        print 70*'='
        log.critical('A key is missing in the configuration file: %s' % e)
        raise SystemExit()

    # Get optional options
    try:
        config['echoing_shell'] = conf.getboolean('main', 'echoing_shell')
    except ConfigParser.NoOptionError, e:
        config['echoing_shell'] = False
    
    # Read the node sections
    for node in node_names(config):
        try:
            config[node] = dict(
                    hostname=conf.get(node, 'hostname'),
                    blender=conf.get(node, 'blender'),
                    workdir=conf.get(node, 'workdir'),
                )
        except ConfigParser.NoOptionError, e:
            print __doc__
            print 70*'='
            log.critical('A key is missing in the configuration file: %s' % e)
            raise SystemExit()
        
        # Get optional option
        try:
            config[node]['echoing_shell'] = conf.getboolean(node, 'echoing_shell')
        except ConfigParser.NoOptionError, e:
            config[node]['echoing_shell'] = config['echoing_shell']

    # Set default values for option-settable configuration.
    config['scene'] = None

    return config

def parse_options(required=('-b', '-s', '-e')):
    '''Parses the commandline options.

    Returns the options in a dict.
    '''

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'b:s:e:TS:E')
    except getopt.GetoptError, e:
        print __doc__
        raise SystemExit(str(e))

    opts = dict(opts)
    
    for option in required:
        if option not in opts:
            print __doc__
            raise SystemExit('Option %s is required.' % option)

    if args:
        print __doc__
        raise SystemExit('Unknown argument %s' % args)

    return opts

def non_existing_file(path):
    '''Returns a filename which is ensured not to exist (yet) in the
    path.
    '''

    digest = md5.new('somefile')
    for count in xrange(1000):
        filename = os.path.join(path, digest.hexdigest())
        if not os.path.exists(filename):
            return filename

        random.jumpahead(count)
        letter = random.choice('abcdefghijklmnopqrstuvwxyz')
        digest.update(letter)
    
    raise RuntimeError('Could not find non-existing name')

def banner():
    '''Prints the startup banner'''

    print 60*'='
    print 'Starting Multiblend %s' % __revision__
    print ('Created by %s <%s>' % ( __author__.decode('utf-8'), __email__)).encode('utf-8')
    print __url__
    print 60*'='
    print

def nodelist(test_nodes = True):
    '''Returns a list of approved nodes.'''

    # Build list of nodes. Only append approved nodes.
    nodelist = []
    for nodename in node_names(config):
        node = Node(config, nodename)
        if test_nodes:
            if node.test():
                nodelist.append(node)
                log.info('Approved %s' % node)
            else:
                log.info('Disapproved %s: %s' % node)
        else:
            nodelist.append(node)
            log.info('Added %s without testing.' % node)
    
    return nodelist

def check_options_and_config(options, config, nodes):
    '''Checks the options and config file, to see if there are any
    conflicts.
    '''

    blenderfile = os.path.abspath(os.path.realpath(options['-b']))
    blenderdir = os.path.dirname(blenderfile)

    for node in nodes:
        # Check if the localhost workdir is different from the dir the
        # blender file is stored in.
        if not node.hostname == 'localhost':
            continue

        workdir = os.path.abspath(os.path.realpath(node.workdir))

        if workdir == blenderdir:
            log.critical('Directory of %s is the same as the '
                    'work directory for the master node. This is '
                    'not allowed.' % options['-b'])
            raise SystemExit()

def set_scene(config, options):
    '''Sets the 'scene' config key from the -S option'''

    if '-S' in options:
        config['scene'] = options['-S']
        log.info('Rendering scene %s' % config['scene'])

def create_frame_dispatcher(options, config, node_count):
    '''Creates a frame dispatcher for the given configuration and commandline
    options.
    '''

    # Get options, calculate chunk size, and create frame dispatcher.
    start = int(options['-s'])
    end = int(options['-e'])
    frames = end - start + 1
    chunksize = max(1, min(config['chunks'], frames / node_count))

    # Figure out whether we need to check the output path
    fd_output_path = '-E' in options and config['outputpath'] or ''
    return FrameDispatcher(start, end, chunksize, fd_output_path)

def distrib_cache():
    '''Distributes the cache directory belonging to the blend file to
    the working directory of the nodes.
    '''

    global config

    banner()

    config = load_config()
    options = parse_options(required=('-b', ))

    log.info('Distributing cache files for file: %s' % options['-b'])

    cache_dir = 'blendcache_%s' % os.path.splitext(options['-b'])[0]
    log.debug('Cache dir: %s' % cache_dir)

    # Get list of nodes.
    nodes = nodelist('-T' not in options)
    if not nodes:
        log.error('No nodes available')
        raise SystemExit()
    
    for node in nodes:
        log.info('Syncing to %s' % node)
        target = '%s:%s%s' % (node.hostname, node.workdir, os.path.sep)
        rsync = DebuggingPopen(node.log, ('rsync', cache_dir, target,
            '-va', '--delete'))
        rsync.tochild.close()

        for line in rsync.fromchild:
            log.debug(line.strip())
        rsync.fromchild.close()
        rsync.wait()


def main():
    '''Runs multiblend'''

    global config

    start_time = datetime.datetime.now()

    banner()

    config = load_config()
    options = parse_options()

    # Get list of nodes.
    nodes = nodelist('-T' not in options)
    if not nodes:
        log.error('No nodes available')
        raise SystemExit()

    check_options_and_config(options, config, nodes)
    dispatcher = create_frame_dispatcher(options, config, len(nodes))

    # Start nodes
    for node in nodes:
        node.renderchunks(
            options['-b'],
            dispatcher
        )
    
    try:
        # Give nodes some time to start
        time.sleep(2)

        # Wait for nodes to finish
        done = False
        while not done:
            done = True

            # Check the nodes
            for node in nodes:
                # If one node is still rendering, we're not done.
                if node.rendering:
                    done = False
                    break

            # Wait a while before checking again.
            time.sleep(1)
    except KeyboardInterrupt:
        log.info('Ctrl+C pressed, trying to stop them all. '
                'Please be patient.')
        for node in nodes:
            node.abort()
        
    time.sleep(2)
    log.info('Done multiblendering.')

    end_time = datetime.datetime.now()

    log.info('Start time: %s' % start_time)
    log.info('End time  : %s' % end_time)
    log.info('Spent     : %s' % (end_time - start_time))

if __name__ == '__main__':
    main()

# vim:tabstop=4 expandtab foldnestmax=2
