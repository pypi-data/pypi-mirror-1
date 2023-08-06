##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: tests.py 106612 2009-12-16 02:10:27Z srichter $
"""
__docformat__ = "reStructuredText"
import logging
import os
import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

class TestingHandler(logging.Handler):

    def emit(self, record):
        print record.msg

handler = TestingHandler()

def do_cmd(cmd):
    os.system(cmd)

def setUp(test):
    logging.getLogger().addHandler(handler)

def tearDown(test):
    logging.getLogger().removeHandler(handler)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            globs={'cmd': do_cmd},
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
