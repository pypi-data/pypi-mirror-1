#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Yamlog Authors
# Use of this source code is governed by the ISC License (LICENSE file).

import os

import yamlog


def setup_package():
    """Will be executed before tests are run."""
    here = os.path.abspath(os.path.dirname(__file__))
    file_ = os.path.join(here, 'python.log')

    yamlog.setup(file_)


def teardown_package():
    """Will be executed after all tests have run."""
    yamlog.teardown()
