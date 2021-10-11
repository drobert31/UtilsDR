#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script Permettant de logguer.

Ce Module Permet de mettre dans un fichier de log :

Notes:
------
Inspiré de :
    https://realnitinworks.netlify.app/decorator-saves-logging.html#decorator-saves-logging
"""

import logging
import inspect

# Choisir les modules a exporter
__all__ = ['initLog', 'LOG_DEBUG', 'LOG_INFO', 'LOG_ERROR', 'LOG_WARN']


def caller_prefix(func):
    """
    This decorator function modifies log message
    to include the actual calling function name and line number
    in the message.
    """

    # @wraps(func)
    def wrapper(*args, **kwargs):
        # 1: represents line at the caller
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)

        # Prefixes the function name and line number to the actual message(args[0])
        # args[1:] - concatenate to make sure we don't lose it after manipulating args
        filename = info.filename.split('/')[-1]
        args = (
            f'{filename} {info.function}:{info.lineno}: {args[0]}', ) + args[1:]

        func(*args, **kwargs)

    return wrapper


def initLog(app='app'):
    """Initialisation du fichier de log.

    TODO:
    -----
    Creer le fichier de log.
    """
    logging.basicConfig(
        filename='/var/log/Python/' + app + '.log',
        level=logging.DEBUG,
        format="%(asctime)-15s %(filename)s %(funcName)s %(levelname)s:%(message)s"
    )


@caller_prefix
def LOG_DEBUG(msg):
    logging.debug(msg)


@caller_prefix
def LOG_INFO(msg):
    logging.info(msg)


@caller_prefix
def LOG_ERROR(msg):
    logging.error(msg)


@caller_prefix
def LOG_WARN(msg):
    logging.warning(msg)
