import subprocess
import os
import sys
import argparse
import argh
import requests
from argh import arg, aliases, named
from glob import glob

home = os.path.expanduser('~')
storage = '{home}/.groupthink'.format(home=home)
if sys.platform.find('win') == 0:
    dest = '{home}/bin'.format(home=home)
else:
    dest = '/usr/local/bin'


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
    script_exists = os.path.exists('{dest}/{alias}'.format(dest=dest, alias=alias))
    if script_exists:
        message = []
        message.append('A script is already installed with the name {alias}.'.format(alias=alias))
        message.append('You can try to install {org}-cli under a different name, with:\n'.format(org=org))
        message.append('  groupthink --install {org} --alias [alias]'.format(org=org))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', storage])
        execute_cmd(['mkdir', '-p', dest])
        repo_url = 'https://github.com/{org}/{org}-cli.git'.format(org=org)
        repo_dest = '{storage}/{alias}-cli'.format(storage=storage, alias=alias)
        if requests.get(repo_url[:-4]).status_code < 400:
            (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
            if err.find('fatal: ') > -1:
                # return 'Could not get {org}-cli command. Please make sure https://github.com/{org}/{org}-cli exists.'.format(org=org)
                sys.exit(1)
        else:
            return 'Could not get {org}-cli command. Please make sure https://github.com/{org}/{org}-cli exists.'.format(org=org)
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


@arg('org', help='The org to uninstall')
@arg('-d','--dest')
@arg('-s', '--storage')
def uninstall(org, dest=dest, storage=storage):
    """
    Removes an org's CLI scripts.
    """
    # remove org scripts repo and groupthink script
    check_install(org, check_already=True, storage=storage)
    execute_cmd(['rm', '-rf', '{storage}/{org}-cli'.format(storage=storage, org=org)])
    execute_cmd(['rm', '{dest}/{org}'.format(dest=dest, org=org)])
    return 'Removed {org} command.'.format(org=org)


@arg('org', help='The org to update', nargs='?')
@arg('-d','--dest')
@arg('-s', '--storage')
def update(org, dest=dest, storage=storage):
    """
    Checks if there are updates to an org's installed CLI scripts.
    """
    # check if there are any updates to the scripts repository
    installed = installed_orgs(storage)
    if org == None:
        for org in installed:
            do_update(org, dest, storage)
    else:
        do_update(org, dest, storage)


def do_update(org, dest=dest, storage=storage):
    check_install(org, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg or err.find('From') == 0:
        return 'There are updates to the {org} command. Use the --upgrade subcommand to add them'.format(org=org)
    else:
        return 'Your {org} command is already up to date.'.format(org=org)


@arg('org', help='The org to upgrade', nargs='?')
@arg('-d','--dest')
@arg('-s', '--storage')
def upgrade(org, dest=dest, storage=storage):
    """
    Updates an org's installed CLI scripts.
    """
    # upgrade org scripts repository
    installed = installed_orgs(storage)
    if org == None:
        for org in installed:
            do_upgrade(org, dest, storage)
    else:
        do_upgrade(org, dest, storage)


def do_upgrade(org, dest=dest, storage=storage):
    check_install(org, check_already=True, storage=storage)
    upgrade_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'pull']
    (msg, err) = execute_cmd(upgrade_cmd)
    if msg.find('Already up-to-date') > -1:
        return 'Your {org} command is already up to date.'.format(org=org)
    else:
        return 'Upgraded {org} command.'.format(org=org)


@aliases('installed')
@named('list')
@arg('-s','--storage')
def list_orgs(storage=storage):
    """
    Lists all org CLI scripts you have installed.
    """
    # print out a list of orgs whose scripts have been
    # installed to ~/.groupthink
    installed = installed_orgs(storage)


def installed_orgs(storage=storage):
    # return a list of organization whose scripts have been installed
    # to ~/.groupthink
    installed = []
    for org in glob('{}/*/'.format(storage)):
        org_path = os.path.normpath(org)
        org_name = org_path.rstrip(os.sep).split(os.sep)[-1]
        if org_name.find('-cli') > 0:
            installed.append(org_name.split('-cli')[0])
    return installed


def check_install(org, check_already=True, storage=storage):
    # check if org-cli repo already installed in ~/.groupthink
    installed = org in installed_orgs(storage)
    if not installed and check_already:
        print('Error: {org} command not installed. You can try to install it with:\n'.format(org=org))
        print('  groupthink --install {org}'.format(org=org))
        sys.exit(1)
    elif installed and not check_already:
        print('Error: {org} command already installed. You can check for updates with:\n'.format(org=org))
        print('  groupthink --update {org}'.format(org=org))
        sys.exit(1)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main(argv=sys.argv):
    parser = argh.ArghParser( description='Install a GitHub org\'s set of CLI tools, as defined at https://github.com/<org>/<org>-cli')
    parser.add_commands([install, uninstall, upgrade, update, list_orgs])
    parser.dispatch()
