##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the zpasswd script.

$Id: test_zpasswd.py 70794 2006-10-19 04:29:42Z baijum $
"""

import os
import unittest

from zope.testing.doctestunit import DocTestSuite

from zope.app.authentication import password
from zope.app.server.tests.test_mkzopeinstance import TestBase

from zope.app.server import zpasswd


class ArgumentParsingTestCase(TestBase):

    config = os.path.join(os.path.dirname(__file__), "site.zcml")

    def parse_args(self, args):
        argv = ["foo/bar.py"] + args
        options = zpasswd.parse_args(argv)
        self.assertEqual(options.program, "bar.py")
        self.assert_(options.version)
        return options

    def check_stdout_content(self, args):
        try:
            options = self.parse_args(args)
        except SystemExit, e:
            self.assertEqual(e.code, 0)
            self.assert_(self.stdout.getvalue())
            self.failIf(self.stderr.getvalue())
        else:
            self.fail("expected SystemExit")

    def test_no_arguments(self):
        options = self.parse_args([])
        self.assert_(options.managers)
        self.assert_(not options.destination)

    def test_version_long(self):
        self.check_stdout_content(["--version"])

    def test_help_long(self):
        self.check_stdout_content(["--help"])

    def test_help_short(self):
        self.check_stdout_content(["-h"])

    def test_destination_short(self):
        options = self.parse_args(["-o", "filename"])
        self.assertEqual(options.destination, "filename")

    def test_destination_long(self):
        options = self.parse_args(["--output", "filename"])
        self.assertEqual(options.destination, "filename")

    def test_config_short(self):
        options = self.parse_args(["-c", self.config])
        self.assert_(options.managers)

    def test_config_long(self):
        options = self.parse_args(["--config", self.config])
        self.assert_(options.managers)

class ControlledInputApplication(zpasswd.Application):

    def __init__(self, options, input_lines):
        super(ControlledInputApplication, self).__init__(options)
        self.__input = input_lines

    def read_input_line(self, prompt):
        return self.__input.pop(0)

    read_password = read_input_line

    def all_input_consumed(self):
        return not self.__input

class Options(object):

    config = None
    destination = None
    version = "[test-version]"
    program = "[test-program]"
    managers = password.managers

class InputCollectionTestCase(TestBase):

    def createOptions(self):
        return Options()

    def check_principal(self, expected):
        output = self.stdout.getvalue()
        self.failUnless(output)

        principal_lines = output.splitlines()[-(len(expected) + 1):-1]
        for line, expline in zip(principal_lines, expected):
            self.failUnlessEqual(line.strip(), expline)

    def test_principal_information(self):
        options = self.createOptions()
        app = ControlledInputApplication(options,
            ["id", "title", "login", "1", "passwd", "passwd", "description"])
        app.process()
        self.failUnless(not self.stderr.getvalue())
        self.failUnless(app.all_input_consumed())
        self.check_principal([
            '<principal',
            'id="id"',
            'title="title"',
            'login="login"',
            'password="passwd"',
            'description="description"',
            '/>'
            ])


def test_suite():
    suite = DocTestSuite('zope.app.server.zpasswd')
    suite.addTest(unittest.makeSuite(ArgumentParsingTestCase))
    suite.addTest(unittest.makeSuite(InputCollectionTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
