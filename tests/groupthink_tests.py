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
    global home, repo_dir
    home = os.path.expanduser('~')
    repo_dir = '{}/.groupthink-test'.format(home)
    execute_cmd(['mkdir', '-p', repo_dir])


def tearDown():
    execute_cmd(['rm', '-rf', repo_dir])


def test_has_proper_version():
    eq_(__version__, '0.1.1')


def test_installs():
    install('dcgov', script_dir=repo_dir, repo_dir=repo_dir)
    eq_(os.path.exists('{}/dcgov-cli'.format(repo_dir)), True)
    eq_(os.path.exists('{}/dcgov'.format(repo_dir)), True)


def test_installed_orgs():
    installed = installed_orgs(repo_dir=repo_dir)
    eq_('dcgov' in installed, True)
    eq_('18f' in installed, False)


def test_execute_cmd():
    (out, err) = execute_cmd(['echo', 'hello'])
    eq_(out.find('hello') == 0, True)
    eq_(err, '')


def test_update():
    output = update('dcgov', script_dir=repo_dir, repo_dir=repo_dir)
    eq_(output, 'Your dcgov command is already up to date.')


def test_upgrades():
    output = upgrade('dcgov', script_dir=repo_dir, repo_dir=repo_dir)
    eq_(output, 'Your dcgov command is already up to date.')


def test_lists():
    output = list_orgs(repo_dir=repo_dir)
    eq_(output.find('- dcgov') > -1, True)


def test_uninstalls():
    uninstall('dcgov', script_dir=repo_dir, repo_dir=repo_dir)
    eq_(os.path.exists('{}/dcgov-cli'.format(repo_dir)), False)
    eq_(os.path.exists('{}/dcgov'.format(repo_dir)), False)
