#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Yamlog Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
Throw - log exceptions before being raised.
"""

__all__ = ['Throw']

import logging
import traceback

from . import logger


class Throw(object):
    """Throw an `exception` which is logged.

    ...

    Parameters
    ----------
    logger : class of `yamlog.logger()`
        The instace of the logger.
    background : boolean, optional
        If *True*, the exceptions are not raised else that they are
        logged. Useful for daemons or other background processes.
        Default is *False*.

    Attributes
    ----------
    logger
    background

    """

    def __init__(self, logger, background=False):
        self.background = background
        self.logger = logger

    def __call__(self, exception, *args):
        """Throw an `exception` passing it the arguments from `args`.

        The exception is caught to log it if the command is being run
        in the background.

        ...

        Parameters
        ----------
        exception : class
            The name of the exception to throw.
        args : tuple of str
            The arguments to pass to the exception.

        Returns
        -------
        int
            The error exit code (*1*); if `background` is *True*.

        Raises
        ------
        exception
            The same exception with that was called; if `background` is
            *False*.

        """

        try:
            raise exception(*args)
        except exception as err:
            #self.logger.exception(repr(err))

            # Trying to simulate `logging.exception()`.
            caller = _caller()
            message = "File \"{0}\", line {1}, in {2}\n {3}".format(
                caller[0], caller[1], caller[2], caller[3])

            self.logger.error(repr(err))
            self.logger.debug('Traceback: ' + message)

            #_log = logging.LogRecord('name', 'ERROR', caller[0], caller[1],
                                     #'', '', None, None)
            #self.logger.error(_log.getMessage())

            if not self.background:
                raise exception(str(err))
            else:
                return 1


def _caller(up=1):
    """Get information about the caller function.

    ...

    Parameters
    ----------
    up : int, optional
        Allow retrieval of a caller further back up into the call stack.
        Default is *1*.

    Returns
    -------
    frame : tuple of str, int, str, str
        File name, line number, function name and source text of the
        caller's caller.

    Notes
    -----
    The source text may be *None* and function name may be *?* in the
    returned result. In Python 2.3+ the file name may be an absolute
    path.

    """
    try:  # Just get a few frames.
        frame = traceback.extract_stack(limit=up+2)
        if frame:
            return frame[0]
    except:
        if __debug__:
            traceback.print_exc()
        pass
    # Running with Psyco?
    return ('', 0, '', None)


# http://www.python.org/dev/peps/pep-0344/
