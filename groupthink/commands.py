# -*- codes: utf-8 -*-

from __future__ import print_function

import subprocess
import os
import sys
from glob import glob

import requests
from argh import arg, aliases, named, ArghParser

home = os.path.expanduser('~')
storage = '{home}/.groupthink'.format(home=home)
if sys.platform.find('win') == 0:
    dest = '{home}/bin'.format(home=home)
else:
    dest = '/usr/local/bin'


@arg('org', help='The org command you want to install')
@arg('-a', '--alias', help='Set a name for this command')
@arg('-d', '--dest', help='Choose a directory on your PATH to install this command')
def install(org, alias=None, dest=dest):
    """
    Provided a GitHub org name, installs that org's CLI scripts.
    """
    alias = alias if alias else org
    check_install(alias, check_already=False, storage=storage)
    script_exists = os.path.exists('{dest}/{alias}'.format(dest=dest, alias=alias))
    if script_exists:
        message = []
        message.append('A script is already installed with the name {alias}.'.format(alias=alias))
        message.append('You can try to install {org}-cli under a different name, with:\n'.format(org=org))
        message.append('  groupthink install {org} --alias [alias]'.format(org=org))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', storage])
        execute_cmd(['mkdir', '-p', dest])
        repo_url = 'https://github.com/{org}/{org}-cli.git'.format(org=org)
        repo_dest = '{storage}/{alias}-cli'.format(storage=storage, alias=alias)
        if requests.get(repo_url[:-4]).status_code < 400:
            (out, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
            if err.find('fatal: ') > -1:
                sys.exit(1)
        else:
            sys.exit(1)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{dest}/{alias}'.format(dest=dest, alias=alias)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        if org == alias:
            return 'Installed {org} command.'.format(org=org)
        else:
            return 'Installed {org} command under the alias {alias}.'.format(org=org, alias=alias)
    except:
        return 'Could not get {org}-cli command. Please make sure https://github.com/{org}/{org}-cli exists.'.format(org=org)


@arg('org', help='The command to uninstall')
@arg('-d', '--dest', help='The directory where you installed this command')
def uninstall(org, dest=dest):
    """
    Removes an org's CLI scripts.
    """
    check_install(org, check_already=True, storage=storage)
    execute_cmd(['rm', '-rf', '{storage}/{org}-cli'.format(storage=storage, org=org)])
    execute_cmd(['rm', '{dest}/{org}'.format(dest=dest, org=org)])
    return 'Removed {org} command.'.format(org=org)


@arg('org', help='The command to update. Leave empty to update all commands.', nargs='?')
@arg('-d', '--dest', help='The directory where you installed the command(s)')
def update(org, dest=dest):
    """
    Checks for updates to an org's installed CLI scripts.
    """
    if not org:
        installed = installed_orgs(storage)
        for org in installed:
            print(do_update(org, dest, storage))
    else:
        print(do_update(org, dest, storage))


def do_update(org, dest=dest, storage=storage):
    """
    Checks for updates for a given command's cli repo with a git fetch
    """
    check_install(org, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'fetch']
    (out, err) = execute_cmd(update_cmd)
    if out or err.find('From') == 0:
        return 'There are updates to the {org} command. Use the upgrade subcommand to add them'.format(org=org)
    else:
        return 'Your {org} command is already up to date.'.format(org=org)


@arg('org', help='The command to upgrade. Leave empty to upgrade all commands.', nargs='?')
@arg('-d', '--dest', help='The directory where you installed the command(s)')
def upgrade(org, dest=dest):
    """
    Upgrades an org's installed CLI scripts.
    """
    if not org:
        installed = installed_orgs(storage)
        for org in installed:
            print(do_upgrade(org, dest, storage))
    else:
        print(do_upgrade(org, dest, storage))


def do_upgrade(org, dest=dest, storage=storage):
    """
    Upgrades a given command's cli repo with a git pull
    """
    check_install(org, check_already=True, storage=storage)
    upgrade_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'pull']
    (out, err) = execute_cmd(upgrade_cmd)
    if out.find('Already up-to-date') > -1:
        return 'Your {org} command is already up to date.'.format(org=org)
    else:
        return 'Upgraded {org} command.'.format(org=org)


@aliases('installed')
@named('list')
def list_orgs():
    """
    Lists all org CLI scripts you have installed.
    """
    installed = installed_orgs(storage)
    message = []
    if installed:
        message.append('You have installed these scripts:\n')
        for org in installed:
            message.append('  - {org}'.format(org=org))
    else:
        message.append('You haven\'t installed any scripts. Install one with:\n')
        message.append('  groupthink install <org>')
    return '\n'.join(message)


def installed_orgs(storage=storage):
    """
    Returns a list of organization whose scripts have been installed
    to ~/.groupthink
    """
    installed = []
    for org in glob('{}/*/'.format(storage)):
        org_path = os.path.normpath(org)
        org_name = org_path.rstrip(os.sep).split(os.sep)[-1]
        if org_name.find('-cli') > 0:
            installed.append(org_name.split('-cli')[0])
    return installed


def check_install(org, check_already=True, storage=storage):
    """
    Checks if org-cli repo already installed in ~/.groupthink
    """
    installed = org in installed_orgs(storage)
    if not installed and check_already:
        print('Error: {org} command not installed. You can try to install it with:\n'.format(org=org))
        print('  groupthink install {org}'.format(org=org))
        sys.exit(1)
    elif installed and not check_already:
        print('Error: {org} command already installed. You can check for updates with:\n'.format(org=org))
        print('  groupthink update {org}'.format(org=org))
        sys.exit(1)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main():
    parser = ArghParser(description='Install a GitHub org\'s set of CLI tools, as defined at https://github.com/<org>/<org>-cli')
    parser.add_commands([install, uninstall, upgrade, update, list_orgs])
    parser.dispatch()
