#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of groupthink.
# https://github.com/dcgov/groupthink

# This project is in the public domain within the United States.
# Additionally, the Government of the District of Columbia waives
# copyright and related rights in the work worldwide through the CC0 1.0
# Universal public domain dedication.

import os
import sys
from nose.tools import *

from groupthink import __version__
from groupthink.commands import *

if sys.version_info[:2] < (3, 0):
    from StringIO import StringIO
else:
    from io import StringIO


def setUp():
    global home, storage
    home = os.path.expanduser('~')
    storage = '{}/.groupthink-test'.format(home)
    execute_cmd(['mkdir', '-p', storage])


def tearDown():
    execute_cmd(['rm', '-rf', storage])


def test_has_proper_version():
    eq_(__version__, '0.1.1')


def test_installs():
    install('dcgov', alias='foo', dest=storage, storage=storage)
    eq_(os.path.exists('{storage}/foo-cli'.format(storage=storage)), True)
    eq_(os.path.exists('{storage}/foo'.format(storage=storage)), True)


def test_installed_orgs():
    installed = installed_orgs(storage=storage)
    eq_('foo' in installed, True)
    eq_('dcgov' in installed, False)


def test_execute_cmd():
    (out, err) = execute_cmd(['echo', 'hello'])
    eq_(out.find('hello') == 0, True)
    eq_(err, '')


def test_update():
    output = update('foo', dest=storage, storage=storage)
    eq_(output, 'Your foo command is already up to date.')


def test_upgrades():
    output = upgrade('foo', dest=storage, storage=storage)
    eq_(output, 'Your foo command is already up to date.')


def test_lists():
    output = list_orgs(storage=storage)
    eq_(output.find('- foo') > -1, True)


def test_uninstalls():
    uninstall('foo', dest=storage, storage=storage)
    eq_(os.path.exists('{storage}/foo-cli'.format(storage=storage)), False)
    eq_(os.path.exists('{storage}/foo'.format(storage=storage)), False)
