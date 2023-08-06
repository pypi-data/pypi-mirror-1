#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Yamlog Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for command tools."""

from nose import tools

import yamlog

_log = yamlog.logger(__name__)


class LogTestError(Exception):
    pass


class TestException(object):
    throw = yamlog.Throw(_log)
    throw_bg = yamlog.Throw(_log, background=True)

    @tools.raises(LogTestError)
    def test_log_exception(self):
        self.throw(LogTestError, 'Exception caught and logged')

    def test_log_exception_background(self):
        assert 1 == self.throw_bg(LogTestError,
                                  'Exception caught and logged on background')
