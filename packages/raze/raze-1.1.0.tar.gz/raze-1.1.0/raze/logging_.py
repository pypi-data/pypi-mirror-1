"""
RAZE Python Libraries
Extensions to the standard logging module.


RAZE - Copyright (c) 2006 James Harris, Erin Houston
$Id: logging_.py 258 2006-11-23 01:40:07Z james $
"""
__revision__ = "$Revision: 258 $"
__location__ = "$URL: http://icecave.svn.net.au/dav/lib/raze/tags/raze-1.1.0/raze/logging_.py $"
__all__ = [ 'Loggable' ]

from logging import *
from protocols import advise, AbstractBase


class Loggable(AbstractBase):
    """ Interface for objects that provide logging. """
    @classmethod
    def log_facility(class_):
        """ 
        The facility to log messages to. This method is designed to be 
        overridden, it need not be a class method.
        """
        return class_.__module__

    @property
    def logger(self):
        """ Retreive this objects logger. """
        return getLogger(self.log_facility())

    def format_log_message(self, message):
        """ Format the log message before logging it. """
        if message is None:
            return repr(self)
        return '%r: %s' % (self, message)

    def log_debug(self, *pos, **kw):
        """ Log a DEBUG message. """
        return self.log(DEBUG, *pos, **kw)

    def log_info(self, *pos, **kw):
        """ Log an INFO message. """
        return self.log(INFO, *pos, **kw)

    def log_warning(self, *pos, **kw):
        """ Log a WARNING message. """
        return self.log(WARNING, *pos, **kw)
    
    def log_error(self, *pos, **kw):
        """ Log an ERROR message. """
        return self.log(ERROR, *pos, **kw)
    
    def log_critical(self, *pos, **kw):
        """ Log a CRITICAL message. """
        return self.log(CRITICAL, *pos, **kw)
    
    def log_exception(self, message=None, level=DEBUG):
        """ Log a details of the current exception. """
        from sys import exc_info
        return self.log(level, message, exc_info=exc_info())

    def log(self, level, message, *pos, **kw):
        """ Log a message. """
        message = self.format_log_message(message)
        return self.logger.log(level, message, *pos, **kw)


class LoggableAdapter(Loggable):
    """ Adapts regular objects to provide a loggable interface. """
    advise(instancesProvide  = [ Loggable ],
           asAdapterForTypes = [ object ])

    def __init__(self, object):
        self.object = object

    @property
    def log_facility(self):
        """ The facility to log messages to. """
        class_ = type(self.object)
        return '%s.%s' % (class_.__module__, class_.__name__)


def _test():
    """ Test this module. """
    import doctest
    import logging_
    return doctest.testmod(logging_)
