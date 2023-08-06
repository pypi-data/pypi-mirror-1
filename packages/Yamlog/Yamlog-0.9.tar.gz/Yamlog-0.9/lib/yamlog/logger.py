#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Yamlog Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
logger - return a logging instance already configured.
setup - setup the logging.
teardown - tear down the logging.
"""

__all__ = ['logger', 'setup', 'teardown']

from logging import handlers
import logging
import os
import platform
import textwrap


class _LoggerAdapter(logging.LoggerAdapter):
    """Prepend an indentation to the logging message.

    Subclass `LoggerAdapter` and override `process()`.

    """
    SPACE = '  '  # 2 chars.
    wrapper = textwrap.TextWrapper(initial_indent=SPACE, subsequent_indent=SPACE)

    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        return self.wrapper.fill(msg), kwargs


class _LoggerExtra(object):
    """The `extra` context information passed to `LoggerAdapter`."""
    host = platform.node()  # The computer's network name.

    def __getitem__(self, name):
        """Allow this instance to look like a dict."""
        if name == 'host':
            result = self.host
        return result

    def __iter__(self):
        """Allow iteration over keys.

        They which will be merged into the `LogRecord` dictionary before
        formatting and output.

        """
        keys = ['host',]
        keys.extend(self.__dict__.keys())
        return iter(keys)  # Better than 'keys.__iter__'


def logger(name):
    """Return an instance of `LoggerAdapter` with the extra fields."""
    return _LoggerAdapter(logging.getLogger(name), _LoggerExtra())


def setup(filename='/tmp/python.log'):
    """Configure the logging.

    ...

    Parameters
    ----------
    filename : str
        The file name where logs are going to be written.
        Default is */tmp/python.log*.

    See Also
    --------
    teardown

    Notes
    -----
    Use the date and time international format:
        http://www.w3.org/TR/NOTE-datetime

    Could be used the directory */var/log* but there would be to run it
    as an user with permissions to write there.

    """
    # If */tmp* doesn't exists (not mounted), then will be used the
    # root directory.
    if os.path.isdir(os.path.dirname(filename)):
        filename_ = filename
    else:
        filename_ = '/' + os.path.basename(filename)

    # The root logger.
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    # File logger
    # -----------
    # Create a file handler with rotation of disk log files at 128K, which
    # logs DEBUG messages or higher.
    file_handler = handlers.RotatingFileHandler(filename_, maxBytes=131072,
                                                backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter in YAML format and add it to the handler.
    yaml_formatter = logging.Formatter(
        "---\n"
        "Date-Time: %(asctime)s\n"
        "Host: %(host)s\n"
        "Name: %(name)s\n"
        "%(levelname)s:\n"
        "%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
    file_handler.setFormatter(yaml_formatter)

    # Console logger
    # --------------
    # Create the console handler with a higher log level which writes to
    # 'sys.stderr'.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # Create a simple formatter.
    simple_formatter = logging.Formatter(
        "%(name)s: %(levelname)s %(message)s")
    console_handler.setFormatter(simple_formatter)

    # Add the handlers to the logger.
    # ---
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Don't collect
    # -------------
    #logging.logMultiprocessing = 0
    logging.logProcesses = 0
    logging.logThreads = 0


def teardown():
    """Flush and close all handlers of logging.

    ...

    See Also
    --------
    setup

    """
    logging.shutdown()
