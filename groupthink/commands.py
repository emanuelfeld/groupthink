import subprocess
import os
import sys
import argparse
from glob import glob


home = os.path.expanduser('~')
storage = '{home}/.groupthink'.format(home=home)
if sys.platform.find('win') == 0:
    dest = '{home}/bin'.format(home=home)
else:
    dest = '/usr/local/bin'


def install(org, alias=None, dest=dest, storage=storage):
    # install organization scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    alias = alias if alias else org
    check_install(alias, check_already=False, storage=storage)
    script_exists = os.path.exists('{dest}/{alias}'.format(dest=dest, alias=alias))
    if script_exists:
        message = []
        message.append('A script is already installed with the name {alias}.'.format(alias=alias))
        message.append('You can try to install {org}-cli under a different name, with:\n'.format(org=org))
        message.append('  groupthink --install {org} --alias name'.format(org=org))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', storage])
        execute_cmd(['mkdir', '-p', dest])
        repo_url = 'https://github.com/{org}/{org}-cli.git'.format(org=org)
        repo_dest = '{storage}/{alias}-cli'.format(storage=storage, alias=alias)
        print(repo_dest)
        (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
        if err.find('fatal: ') > -1:
            sys.exit(1)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{dest}/{alias}'.format(dest=dest, alias=alias)
        print(groupthink_dest)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        if org == alias:
            return 'Installed {org} command.'.format(org=org)
        else:
            return 'Installed {org} command under the alias {alias}.'.format(org=org, alias=alias)            
    except:
        return 'Could not get {org}-cli command. Please make sure https://github.com/{org}/{org}-cli exists.'.format(org=org)


def uninstall(org, dest=dest, storage=storage):
    # remove organization scripts repo and groupthink script
    check_install(org, check_already=True, storage=storage)
    execute_cmd(['rm', '-rf', '{storage}/{org}-cli'.format(storage=storage, org=org)])
    execute_cmd(['rm', '{dest}/{org}'.format(dest=dest, org=org)])
    return 'Removed {org} command.'.format(org=org)


def update(org, dest=dest, storage=storage):
    # check if there are any updates to the scripts repository
    check_install(org, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg or err.find('From') == 0:
        return 'There are updates to the {org} command. Use the --upgrade subcommand to add them'.format(org=org)
    else:
        return 'Your {org} command is already up to date.'.format(org=org)


def upgrade(org, dest=dest, storage=storage):
    # upgrade organization scripts repository
    check_install(org, check_already=True, storage=storage)
    update_cmd = ['git', '--git-dir={storage}/{org}-cli/.git'.format(storage=storage, org=org), 'pull']
    (msg, err) = execute_cmd(update_cmd)
    if msg.find('Already up-to-date') > -1:
        return 'Your {org} command is already up to date.'.format(org=org)
    else:
        return 'Upgraded {org} command.'.format(org=org)


def list_orgs(storage=storage):
    # print out a list of organizations whose scripts have been
    # installed to ~/.groupthink
    installed = installed_orgs(storage)
    message = []
    if installed:
        message.append('You have installed these scripts:\n')
        for org in installed:
            message.append('  - {org}'.format(org=org))
    else:
        message.append('You haven\'t installed any scripts. Install one with:\n')
        message.append('  groupthink --install <org>')
    return '\n'.join(message)


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
    parser = argparse.ArgumentParser(prog='groupthink', description='''Install a GitHub organization's CLI scripts. Given an 
        organization name, <org>, this package looks for and install the scripts contained in a repository with the name 
        <org>-cli.''')
    parser.add_argument('--install', '-i', action='store', dest='install', help='Provided a GitHub organization name, installs that organization\'s CLI scripts.')
    parser.add_argument('--uninstall', '-r', action='store', dest='uninstall', help='Removes an organization\'s CLI scripts.')
    parser.add_argument('--upgrade', '-c', action='store', dest='upgrade', help='Checks if there are updates to an organization\'s installed CLI scripts.')
    parser.add_argument('--update', '-u', action='store', dest='update', help='Updates an organization\'s installed CLI scripts.')
    parser.add_argument('--list', '-l', action='store_true', dest='list', help='Lists all organization CLI scripts you have installed.')
    parser.add_argument('--alias', '-a', action='store', dest='alias', help='The GitHub organization name, if you want to install the command under a different name.')
    args = parser.parse_args(argv[1:])
    args_lim = 2 if args.alias else 1
    args_len = len([d for d in args.__dict__.values() if d])
    if args_len > args_lim:
        print("Error: Too many arguments provided")
        parser.print_help()
    elif args.install:
        print(install(args.install, args.alias))
    elif args.list:
        print(list_orgs())
    elif args.uninstall:
        print(uninstall(args.uninstall))
    elif args.upgrade:
        print(upgrade(args.upgrade))
    elif args.update:
        print(update(args.update))
    elif not args_len:
        parser.print_help()
