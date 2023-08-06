#! /usr/bin/env python
"""
pyjld.logger: cross-platform logger

@author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__version__ = "$Id: logger.py 16 2009-04-01 00:09:14Z jeanlou.dupont $"

__all__ = ['logger', 'xcLogger',]



import sys
import logging
import logging.handlers



def logger( name, include_console = False, include_syslog = False, formatter = None, console_stream = None ):
    """ 
    Returns a simple cross-platform logger
    
    **Usage** ::    
    
        >>> log = logger.logger('my_logger')
        >>> log.info('message')
    """
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s: %(message)s ", )        
        
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s: %(message)s ")

    _logger = logging.getLogger(name)
        
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
    
    * Returns a NTEventLogHandler for win32 platform
    * Returns a SysLogHandler for Unix/Linux platforms
    
    The standard ``SysLogHandler`` from the logging package is more difficult
    to configure as it defaults to using the port ``localhost:514``. 
    """
    if (sys.platform[:3] == 'win'):
        return logging.handlers.NTEventLogHandler( appname )
    
    return logging.handlers.TimedRotatingFileHandler('/var/log/%s.log' % appname)

    #More difficult to configure as it defaults to localhost:514 
    #return logging.handlers.SysLogHandler()         

