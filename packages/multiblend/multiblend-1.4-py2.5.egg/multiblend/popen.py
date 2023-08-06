'''Popen class used to log communications with render nodes.'''

import subprocess

class DebuggingPopen(subprocess.Popen):
    '''Popen class, augmented for debugging and easier I/O. Easier for
    this project, anyway ;-)
    '''

    def __init__(self, log, args):
        self.log = log
        subprocess.Popen.__init__(self, args, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True)

    def send(self, line):
        '''Sends a line of text to the process.

        A newline is appended for your convenience.
        '''

        self.log.debug('Sending: %s' % line)
        print >> self.stdin, line
        self.stdin.flush()
    
    def readline(self):
        '''Returns a line of text from the client.'''

        line = self.stdout.readline()
        stripped = line.strip()
        if stripped:
            self.log.debug('Received: %s' % stripped)

        return line


