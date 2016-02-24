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
import subprocess

if sys.version_info[:2] < (3, 0):
    from StringIO import StringIO
else:
    from io import StringIO


def setUp():
    global home, dot
    home = os.path.expanduser('~')
    dot = '{}/.groupthink-test'.format(home)
    execute_cmd(['mkdir', '-p', dot])


def tearDown():
    execute_cmd(['rm', '-rf', dot])


def test_has_proper_version():
    eq_(__version__, '0.1.0')


def test_installs_command():
    install('dcgov', prefix=dot, dot=dot)
    eq_(os.path.exists('{}/dcgov-cli'.format(dot)), True)
    eq_(os.path.exists('{}/dcgov'.format(dot)), True)


def test_update_command():
    out = StringIO()
    update('dcgov', out=out, prefix=dot, dot=dot)
    output = out.getvalue().strip()
    eq_(output, 'Your dcgov command is already up to date.')
    sys.stdout.flush()


def test_upgrades_command():
    out = StringIO()
    upgrade('dcgov', out=out, prefix=dot, dot=dot)
    output = out.getvalue().strip()
    eq_(output, 'Your dcgov command is already up to date.')
    sys.stdout.flush()


def test_lists_command():
    out = StringIO()
    list_orgs(out=out, prefix=dot, dot=dot)
    output = out.getvalue().strip()
    eq_(output.find('- dcgov') > -1, True)
    sys.stdout.flush()


def test_uninstalls_command():
    out = StringIO()
    uninstall('dcgov', out=out, prefix=dot, dot=dot)
    eq_(os.path.exists('{}/dcgov-cli'.format(dot)), False)
    eq_(os.path.exists('{}/dcgov'.format(dot)), False)
    sys.stdout.flush()
