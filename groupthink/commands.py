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

@arg('group', help='The group to install')
@arg('-a','--alias', help='Set a different name for this command')
@arg('-d','--dest')
@arg('-s', '--storage')
def install(group, alias=None, dest=dest, storage=storage):
    # install group scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    alias = alias if alias else group
    check_install(alias, check_already=False, storage=storage)
    script_exists = os.path.exists('{0}/{1}'.format(dest, alias))
    if script_exists:
        message = []
        message.append('A script is already installed with the name {0}.'.format(alias))
        message.append('You can try to install {0}-cli under a different name, with:\n'.format(group))
        message.append('  groupthink install {0} --alias ALIAS'.format(group))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', storage])
        repo_url = 'https://github.com/{0}/{0}-cli.git'.format(group)
        repo_dest = '{}/{}-cli'.format(storage, group)
        if requests.get(repo_url[:-4]).status_code < 400:
            (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
            if err.find('fatal: ') > -1:
                return '{0}-cli is already installed. Remove it before creating an aliased command.'.format(group)
                sys.exit(1)
        else:
            return 'Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.'.format(group)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{}/{}'.format(dest, alias)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        return 'Installed {} command.'.format(group)
    except:
        return 'Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.'.format(group)


@arg('group', help='The group to uninstall')
@arg('-d','--dest')
@arg('-s', '--storage')
def uninstall(group, dest=dest, storage=storage):
    # remove group scripts repo and groupthink script
    check_install(group, check_already=True, storage=storage)
    execute_cmd(['rm', '-rf', '{0}/{1}-cli'.format(storage, group)])
    execute_cmd(['rm', '{0}/{1}'.format(dest, group)])
    return 'Removed {} command.'.format(group)


@arg('group', help='The group to update')
@arg('-d','--dest')
@arg('-s', '--storage')
def update(group, dest=dest, storage=storage):
    # check if there are any updates to the scripts repository
    check_install(group, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(storage, group), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg:
        return 'There are updates to the {0} command. Use the upgrade subcommand to add them'.format(group)
    else:
        return 'Your {0} command is already up to date.'.format(group)


@arg('group', help='The group to upgrade')
@arg('-d','--dest')
@arg('-s', '--storage')
def upgrade(group, dest=dest, storage=storage):
    # upgrade group scripts repository

    check_install(group, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(storage, group), 'pull']
    (msg, err) = execute_cmd(update_cmd)
    if msg.find('Already up-to-date') > -1:
        return 'Your {0} command is already up to date.'.format(group)
    else:
        return 'Upgraded {} command.'.format(group)


@aliases('list')
@arg('-s','--storage')
def installed(storage=storage):
    # print out a list of groups whose scripts have been
    # installed to ~/.groupthink
    installed = installed_groups(storage)
    message = []
    if installed:
        message.append('You have installed these scripts:\n')
        for group in installed:
            message.append('  - {}'.format(group))
    else:
        message.append('You haven\'t installed any scripts. Install one with:\n')
        message.append('  groupthink install <group>')
    return '\n'.join(message)


def installed_groups(storage=storage):
    # return a list of group whose scripts have been installed
    # to ~/.groupthink
    installed = []
    for group in glob('{}/*/'.format(storage)):
        group_name = group.rstrip('/').split('/')[-1]
        if group_name.find('-cli') > 0:
            installed.append(group_name.split('-cli')[0])
    return installed


def check_install(group, check_already=True, storage=storage):
    # check if group-cli repo already installed in ~/.groupthink
    installed = group in installed_groups(storage)
    if not installed and check_already:
        print('Error: {0} command not installed. You can try to install it with:\n'.format(group))
        print('  groupthink install {0}'.format(group))
        sys.exit(0)
    elif installed and not check_already:
        print('Error: {0} command already installed. You can check for updates with:\n'.format(group))
        print('  groupthink update {0}'.format(group))
        sys.exit(0)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main(argv=sys.argv):
    parser = argh.ArghParser()
    parser.add_commands([install, uninstall, upgrade, update, installed])
    parser.dispatch()
    # parser = argparse.ArgumentParser(prog='groupthink', description='''Install a GitHub group's CLI scripts. Given an
    #     group name, <group>, this package looks for and install the scripts contained in a repository with the name
    #     <org>-cli.''')
    # parser.add_argument('--install', '-i', action='store', dest='install', help='Provided a GitHub group name, installs that group's CLI scripts.')
    # parser.add_argument('--uninstall', '-r', action='store', dest='uninstall', help='Removes an group's CLI scripts.')
    # parser.add_argument('--upgrade', '-c', action='store', dest='upgrade', help='Checks if there are updates to an group's installed CLI scripts.')
    # parser.add_argument('--update', '-u', action='store', dest='update', help='Updates an group's installed CLI scripts.')
    # parser.add_argument('--list', '-l', action='store_true', dest='list', help='Lists all group CLI scripts you have installed.')
    # parser.add_argument('--alias', '-a', action='store', dest='alias', help='The GitHub group name, if you want to install the command under a different name.')
    # args = parser.parse_args(argv[1:])
    # args_lim = 2 if args.alias else 1
    # args_len = len([d for d in args.__dict__.values() if d])
    # if args_len > args_lim:
    #     print('Error: Too many arguments provided')
    #     parser.print_help()
    # elif args.install:
    #     print(install(args.install, args.alias))
    # elif args.list:
    #     print(list_orgs())
    # elif args.uninstall:
    #     print(uninstall(args.uninstall))
    # elif args.upgrade:
    #     print(upgrade(args.upgrade))
    # elif args.update:
    #     print(update(args.update))
    # elif not args_len:
    #     print('Error: You didn't provide any arguments\n')
    #     parser.print_help()
