import subprocess
import os
import sys
import argparse
from glob import glob

script_dir = '/usr/local/bin'
home = os.path.expanduser('~')
repo_dir = '{}/.groupthink'.format(home)


def install(org, alias=None, script_dir=script_dir, repo_dir=repo_dir):
    # install organization scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    alias = alias if alias else org
    check_install(org, check_already=False, repo_dir=repo_dir)
    script_exists = os.path.exists('{0}/{1}'.format(script_dir, org))
    if script_exists:
        message = []
        message.append("A script is already installed with the name {0}.".format(alias))
        message.append("You can try to install {0}-cli under a different name, with:\n".format(org))
        message.append("  groupthink --install name --alias {0}".format(org))
        return '\n'.join(message)
    try:
        execute_cmd(['mkdir', '-p', repo_dir])
        repo_url = 'https://github.com/{0}/{0}-cli.git'.format(alias)
        repo_dest = '{}/{}-cli'.format(repo_dir, org)
        (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
        if err.find('fatal: ') > -1:
            sys.exit(1)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{}/{}'.format(script_dir, org)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        return 'Installed {} command.'.format(org)
    except:
        return "Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.".format(alias)


def uninstall(org, script_dir=script_dir, repo_dir=repo_dir):
    # remove organization scripts repo and groupthink script
    check_install(org, check_already=True, repo_dir=repo_dir)
    execute_cmd(['rm', '-rf', '{0}/{1}-cli'.format(repo_dir, org)])
    execute_cmd(['rm', '{0}/{1}'.format(script_dir, org)])
    return 'Removed {} command.'.format(org)


def update(org, script_dir=script_dir, repo_dir=repo_dir):
    # check if there are any updates to the scripts repository
    check_install(org, check_already=True, repo_dir=repo_dir)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(repo_dir, org), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg or err.find('From') == 0:
        return "There are updates to the {0} command. Use the --upgrade subcommand to add them".format(org)
    else:
        return "Your {0} command is already up to date.".format(org)


def upgrade(org, script_dir=script_dir, repo_dir=repo_dir):
    # upgrade organization scripts repository
    check_install(org, check_already=True, repo_dir=repo_dir)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(repo_dir, org), 'pull']
    (msg, err) = execute_cmd(update_cmd)
    if msg.find('Already up-to-date') > -1:
        return "Your {0} command is already up to date.".format(org)
    else:
        return 'Upgraded {} command.'.format(org)


def list_orgs(repo_dir=repo_dir):
    # print out a list of organizations whose scripts have been
    # installed to ~/.groupthink
    installed = installed_orgs(repo_dir)
    message = []
    if installed:
        message.append("You have installed these scripts:\n")
        for org in installed:
            message.append("  - {}".format(org))
    else:
        message.append("You haven't installed any scripts. Install one with:\n")
        message.append("  groupthink --install <org>")
    return '\n'.join(message)


def installed_orgs(repo_dir=repo_dir):
    # return a list of organization whose scripts have been installed
    # to ~/.groupthink
    installed = []
    for org in glob('{}/*/'.format(repo_dir)):
        org_name = org.rstrip('/').split('/')[-1]
        if org_name.find('-cli') > 0:
            installed.append(org_name.split('-cli')[0])
    return installed


def check_install(org, check_already=True, repo_dir=repo_dir):
    # check if org-cli repo already installed in ~/.groupthink
    installed = org in installed_orgs(repo_dir)
    if not installed and check_already:
        print("Error: {0} command not installed. You can try to install it with:\n".format(org))
        print("  groupthink --install {0}".format(org))
        sys.exit(0)
    elif installed and not check_already:
        print("Error: {0} command already installed. You can check for updates with:\n".format(org))
        print("  groupthink --update {0}".format(org))
        sys.exit(0)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(prog='groupthink', description="""Install a GitHub organization's CLI scripts. Given an 
        organization name, <org>, this package looks for and install the scripts contained in a repository with the name 
        <org>-cli.""")
    parser.add_argument('--install', '-i', action='store', dest='install', help="Provided a GitHub organization name, installs that organization's CLI scripts.")
    parser.add_argument('--uninstall', '-r', action='store', dest='uninstall', help="Removes an organization's CLI scripts.")
    parser.add_argument('--upgrade', '-c', action='store', dest='upgrade', help="Checks if there are updates to an organization's installed CLI scripts.")
    parser.add_argument('--update', '-u', action='store', dest='update', help="Updates an organization's installed CLI scripts.")
    parser.add_argument('--list', '-l', action='store_true', dest='list', help="Lists all organization CLI scripts you have installed.")
    parser.add_argument('--alias', '-a', action='store', dest='alias', help="The GitHub organization name, if you want to install the command under a different name.")
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
        print("Error: You didn't provide any arguments\n")
        parser.print_help()
