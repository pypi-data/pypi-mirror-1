'''More-or-less drop-in replacement for the logging module logger.'''

import sys
import traceback

# The message levels
LEVELS = {
    'DEBUG': 1,
    'INFO': 2,
    'WARN': 3,
    'ERROR': 4,
    'CRITICAL': 5,
    'EXCEPTION': 5,
}

# Inject the levels into this module
module = sys.modules[__name__]
module.__dict__.update(LEVELS)


class Logger(object):

    log_level = INFO

    def __init__(self, name):
        self.name = name

    def logger_builder(logname):
        # Remember at which level this function will log
        logger_level = LEVELS[logname]
        def logger(self, msg):
            '''Logs to level %s''' % logname

            # Log nothing if the level is too low.
            if logger_level < Logger.log_level:
                return

            print '%s %s: %s' % (logname, self.name, msg)
        return logger

    debug = logger_builder('DEBUG')
    info = logger_builder('INFO')
    warn = logger_builder('WARN')
    error = logger_builder('ERROR')
    critical = logger_builder('CRITICAL')
    __exception = logger_builder('EXCEPTION')

    def exception(self, msg):
        '''Logs the message and shows the exception.'''

        self.__exception(msg)
        traceback.print_exc()

def set_level(log_level):
    '''Sets the global log level'''

    Logger.log_level = log_level
