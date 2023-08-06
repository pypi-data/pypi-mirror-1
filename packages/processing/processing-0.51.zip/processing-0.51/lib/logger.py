#
# Module supporting logging 
#
# processing/logger.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

import sys


__all__ = ['enableLogging', 'getLogger', 'subdebug',
           'debug', 'info', 'subwarning', 'warning']

SUBDEBUG = 5
DEBUG = 10
INFO = 20
SUBWARNING = 25
WARNING = 30

_logger = None

def subdebug(msg, *args):
    if _logger:
        _logger.subdebug(msg, *args)

def debug(msg, *args):
    if _logger:
        _logger.debug(msg, *args)

def info(msg, *args):
    if _logger:
        _logger.info(msg, *args)

def subwarning(msg, *args):
    if _logger:
        _logger.subwarning(msg, *args)

def warning(msg, *args):
    if _logger:
        _logger.warning(msg, *args)
    else:
        from processing import currentProcess
        print >>sys.stderr, ('[WARNING/%s] ' + msg) % \
              ((currentProcess().getName(),) + args)


def getLogger():
    '''
    Returns logger used by processing
    '''
    return _logger


def enableLogging(level, HandlerType=None, handlerArgs=(), format=None):
    '''
    Enable logging using `level` as the debug level
    '''
    global _logger
    import logging, atexit
    from processing import process

    logging._acquireLock()
    try:
        if _logger is None:
            _logger = logging.getLogger('processing')
            _logger.propagate = 0

            # we want `_logger` to support the "%(processName)s" format
            def makeRecord(self, *args):
                record = self.__class__.makeRecord(self, *args)
                record.processName = process.currentProcess()._name
                return record
            
            MethodType = type(_logger.log)
            _logger.makeRecord = MethodType(makeRecord, _logger)
            _logger.subdebug = MethodType(_logger.log, SUBDEBUG)
            _logger.subwarning = MethodType(_logger.log, SUBWARNING)
            logging.addLevelName(SUBDEBUG, 'SUBDEBUG')
            logging.addLevelName(SUBWARNING, 'SUBWARNING')

            # cleanup func of `processing` should run before that of `logging`
            atexit._exithandlers.remove((process._exit_func, (), {}))
            atexit._exithandlers.append((process._exit_func, (), {}))

        if not _logger.handlers or HandlerType:
            HandlerType = HandlerType or logging.StreamHandler
            format = format or '[%(levelname)s/%(processName)s] %(message)s'
            handler = HandlerType(*handlerArgs)
            handler.setFormatter(logging.Formatter(format))
            _logger.handlers = [handler]
            _logger.setLevel(level)
            process.currentProcess()._logargs = [
                level, HandlerType, handlerArgs, format
                ]
        else:
            _logger.setLevel(level)
            process.currentProcess()._logargs[0] = level
    finally:
        logging._releaseLock()
