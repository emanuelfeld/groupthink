import subprocess
import os
import sys
import argparse
import argh
import requests
from argh import arg, aliases
from glob import glob

dest = '/usr/local/bin'
home = os.path.expanduser('~')
storage = '{}/.groupthink'.format(home)

@arg('org', help='The org to install')
@arg('-a','--alias', help='Set a different name for this command')
@arg('-d','--dest')
@arg('-s', '--storage')
def install(org, alias=None, dest=dest, storage=storage):
    """
    Provided a GitHub org name, installs that org's CLI scripts.
    """
    # install org scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    alias = alias if alias else org
    check_install(org, check_already=False, storage=storage)
    script_exists = os.path.exists('{0}/{1}'.format(dest, alias))
    if script_exists:
        message = []
        message.append('A script is already installed with the name {0}.'.format(alias))
        message.append('You can try to install {0}-cli under a different name, with:\n'.format(org))
        message.append('  groupthink install {0} --alias ALIAS'.format(org))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', storage])
        repo_url = 'https://github.com/{0}/{0}-cli.git'.format(org)
        repo_dest = '{}/{}-cli'.format(storage, org)
        if requests.get(repo_url[:-4]).status_code < 400:
            (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
            if err.find('fatal: ') > -1:
                return '{0}-cli is already installed. Remove it before creating an aliased command.'.format(org)
                sys.exit(1)
        else:
            return 'Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.'.format(org)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{}/{}'.format(dest, alias)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        return 'Installed {} command.'.format(org)
    except:
        return 'Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.'.format(org)


@arg('org', help='The org to uninstall')
@arg('-d','--dest')
@arg('-s', '--storage')
def uninstall(org, dest=dest, storage=storage):
    """
    Removes an org's CLI scripts.
    """
    # remove org scripts repo and groupthink script
    check_install(org, check_already=True, storage=storage)
    execute_cmd(['rm', '-rf', '{0}/{1}-cli'.format(storage, org)])
    execute_cmd(['rm', '{0}/{1}'.format(dest, org)])
    return 'Removed {} command.'.format(org)


@arg('org', help='The org to update', nargs='?')
@arg('-d','--dest')
@arg('-s', '--storage')
def update(org, dest=dest, storage=storage):
    """
    Checks if there are updates to an org's installed CLI scripts.
    """
    # check if there are any updates to the scripts repository
    installed = installed_groups(storage)
    if org == None:
        for org in installed:
            do_update(org, dest, storage)
    else:
        do_update(org, dest, storage)

def do_update(org, dest=dest, storage=storage):
    check_install(org, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(storage, org), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg:
        print('There are updates to the {0} command. Use the upgrade subcommand to add them'.format(org))
    else:
        print('Your {0} command is already up to date.'.format(org))


@arg('org', help='The org to upgrade', nargs='?')
@arg('-d','--dest')
@arg('-s', '--storage')
def upgrade(org, dest=dest, storage=storage):
    """
    Updates an org's installed CLI scripts.
    """
    # upgrade org scripts repository
    installed = installed_groups(storage)
    if org == None:
        for org in installed:
            do_upgrade(org, dest, storage)
    else:
        do_upgrade(org, dest, storage)


def do_upgrade(org, dest=dest, storage=storage):
    check_install(org, check_already=True, storage=storage)
    upgrade_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(storage, org), 'pull']
    (msg, err) = execute_cmd(upgrade_cmd)
    if msg.find('Already up-to-date') > -1:
        print('Your {0} command is already up to date.'.format(org))
    else:
        print('Upgraded {} command.'.format(org))


@aliases('installed')
@arg('-s','--storage')
def list(storage=storage):
    """
    Lists all org CLI scripts you have installed.
    """
    # print out a list of groups whose scripts have been
    # installed to ~/.groupthink
    installed = installed_groups(storage)
    message = []
    if installed:
        message.append('You have installed these scripts:\n')
        for org in installed:
            message.append('  - {}'.format(org))
    else:
        message.append('You haven\'t installed any scripts. Install one with:\n')
        message.append('  groupthink install <org>')
    return '\n'.join(message)


def installed_groups(storage=storage):
    # return a list of org whose scripts have been installed
    # to ~/.groupthink
    installed = []
    for org in glob('{}/*/'.format(storage)):
        group_name = org.rstrip('/').split('/')[-1]
        if group_name.find('-cli') > 0:
            installed.append(group_name.split('-cli')[0])
    return installed


def check_install(org, check_already=True, storage=storage):
    # check if org-cli repo already installed in ~/.groupthink
    installed = org in installed_groups(storage)
    if not installed and check_already:
        print('Error: {0} command not installed. You can try to install it with:\n'.format(org))
        print('  groupthink install {0}'.format(org))
        sys.exit(0)
    elif installed and not check_already:
        print('Error: {0} command already installed. You can check for updates with:\n'.format(org))
        print('  groupthink update {0}'.format(org))
        sys.exit(0)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main(argv=sys.argv):
    parser = argh.ArghParser()
    parser.add_commands([install, uninstall, upgrade, update, list])
    parser.dispatch()
