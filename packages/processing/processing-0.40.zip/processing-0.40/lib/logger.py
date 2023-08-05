#
# Module supporting logging 
#
# processing/logger.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

import sys
import logging
import atexit

import process          # from . import process


__all__ = ['enableLogging', 'getLogger', 'subdebug', 'debug', 'info', 'note']


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

def note(msg, *args):
    if _logger:
        _logger.note(msg, *args)
    else:
        print >>sys.stderr, ('[NOTE/%s] ' + msg) % \
              ((process.currentProcess().getName(),) + args)


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
    import logging

    logging._acquireLock()
    try:
        if _logger is None:
            _logger = logging.getLogger('processing-7bb69610')
            _logger.propagate = 0

            # we want `_logger` to support the "%(processName)s" format
            def makeRecord(self, *args):
                record = self.__class__.makeRecord(self, *args)
                record.processName = process.currentProcess()._name
                return record
            _logger.makeRecord = makeRecord.__get__(_logger, type(_logger))

            logging.addLevelName(5, 'SUBDEBUG')
            logging.addLevelName(31, 'NOTE')
            _logger.subdebug = process._MethodType(_logger.log, 5)
            _logger.note = process._MethodType(_logger.log, 31)

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
