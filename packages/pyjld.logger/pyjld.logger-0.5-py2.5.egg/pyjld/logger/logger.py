#! /usr/bin/env python
"""
pyjld.logger: cross-platform logging utilities

@author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__version__ = "$Id: logger.py 30 2009-04-02 15:41:05Z jeanlou.dupont $"

__all__ = ['logger', 'xcLogger', 'MsgLogger']


import sys
import logging
import logging.handlers

from string import Template


class Proxy(object):
    """
    Proxy helper
    
    This class is meant to be private to this module.
    """
    #easy way to save space in memory
    __slots__ = ['source', 'target']
    
    def __init__(self, source, target):
        self.source = source
        self.target = target
        
    def __call__(self, *pargs, **kwargs):
        return self.target(self.source, *pargs, **kwargs)




class MsgLogger(object):
    """
    Logger with message look-up and & string.Template functionality
    
    :param name: the logger name
    :param messages: the message look-up dictionary
    :param log: an optional logger (instead of the default one)
    :param template_factory: a template factory for handling the messages
    :param pargs: positional parameters to pass to the __init__ method of the logger
    :param kwargs: keyword parameters to pass to the __init__ method of the logger
    
    The ``logger`` must have the following methods:
    
    * info
    * debug
    * warning
    * error
    * critical

    The :param template_factory: must have a method ``safe_substitute`` to render
    the messages. It defaults to the ``Template`` class from the standard 
    ``string`` module thus supporting parameters through the escape sequence
    starting with the *$* character eg.  *$var*
    
    **Simple usage** ::
    
        >>> import pyjld.logger
        >>> messages = ["msg1":"Message1 [$var]"] 
        >>> ml = pyjld.logger.MsgLogger("app_name", messages)
        >>> ml.info('msg1', var="variable1")
        ... app_name     INFO    : Message1 [variable1]

    """
    # the expected interface of self.logger
    # =====================================
    _logger_methods = ['info', 'debug', 'warning', 'critical', 'error']
    
    def __init__(self, name, messages, log=None, template_factory = None, **kwargs):
        self.messages = messages

        if log:
            self._logger = log
        else:
            self._logger = logger(name, **kwargs)
            
        if template_factory:
            self.template_factory = template_factory
        else:
            self.template_factory = Template

            
    def __getattr__(self, attr):
        """
        Catch method for redirecting access to the logger
        """
        if attr in self._logger_methods:
            return Proxy(attr, self.__handler)
        
        raise AttributeError('attribute [%s] not found in logger' % attr)

    def __handler(self, source, param, **kwargs):

        if self._isExceptionInstance(param):
            rendered = self.__handlerForExceptionClass(exc=param)
        else:
            #no, its just a message_id
            message_id = param
            rendered = self._render(message_id, **kwargs)
        
        method = getattr(self._logger, source)
        
        #invoke the logger with the rendered message
        method(rendered)

    def _isExceptionInstance(self, object):
        try:
            id=object.msg_id
            param=object.params
            return True
        except:
            pass
        
        return False

    def __handlerForExceptionClass(self, exc):
        message_id = exc.msg_id
        params = exc.params
        return self._render(message_id, **params)
        
        
    def _render(self, message_id, **kwargs):
        message = self.__resolveMessageFromId(message_id)
        tpl = self.template_factory(message)
        rendered = tpl.safe_substitute( kwargs )
        return rendered
        

    def __resolveMessageFromId(self, message_id):
        """
        Resolve the human readable message from the ``message_id``
        
        If no corresponding message can be found, the ``message_id`` is used as string.
        
        :param message_id: the message identifier from the ``messages`` dictionary
        """
        default = str( message_id )
        if self.messages:
            return self.messages.get(message_id, default)
        
        return default


def logger( name, include_console = False, include_syslog = False, formatter = None, console_stream = None ):
    """ 
    Returns a simple cross-platform logger
    
    If a logger with ``name`` already exists, its handlers are cleared.
    This behavior is especially useful in daemon environments where the daemonize
    process closes open files and the logging facility must be reinitialized.
    
    **Usage** ::    
    
        >>> log = logger.logger('my_logger')
        >>> log.info('message')
    """
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s: %(message)s ", )        
        
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s: %(message)s ")

    _logger = logging.getLogger(name)
    
    # clear all handlers
    #  This is especially useful in daemon environment
    _logger.handlers = []
    
    if include_syslog:
        syslog = xcLogger( name )
        syslog.setFormatter(formatter)       
        _logger.addHandler(syslog)
        
    if include_console:
        console_stream = console_stream or sys.stdout 
        console = logging.StreamHandler(console_stream)
        console.setFormatter(formatter)
        _logger.addHandler(console)

    return _logger


def xcLogger( appname ):
    """ 
    Cross-platform *syslog* handler
    
    :param appname: the application name to log messages against
    :type appname: string
    
    :rtype: a ``NTEventLogHandler`` for win32 platform OR a ``SysLogHandler`` for Unix/Linux platforms
    
    For Unix/Linux platforms, the filesystem path used is as follows ::
    
        /var/log/$appname.log
    
    The standard ``SysLogHandler`` from the logging package is more difficult
    to configure as it defaults to using the port ``localhost:514``. 
    """
    if (sys.platform[:3] == 'win'):
        return logging.handlers.NTEventLogHandler( appname )
    
    return logging.handlers.TimedRotatingFileHandler('/var/log/%s.log' % appname)

    #More difficult to configure as it defaults to localhost:514 
    #return logging.handlers.SysLogHandler()         

