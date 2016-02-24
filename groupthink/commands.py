import subprocess
import os
import sys
import argparse

prefix = '/usr/local/bin'
home = os.path.expanduser('~')
dot = '{}/.groupthink'.format(home)


def install(org):
    # install organization scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    check_install(org, check_already=False)
    try:
        execute_cmd(['mkdir', '-p', dot])
        repo_url = 'https://github.com/{0}/{0}-cli.git'.format(org)
        repo_dest = '{}/{}-cli'.format(dot, org)
        (out, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
        if err.find('fatal: ') > 0:
            sys.exit(1)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{}/{}'.format(prefix, org)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        print('Installed {} command'.format(org))
    except:
        print("Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists".format(org))


def uninstall(org):
    # remove organization scripts repo and groupthink script
    check_install(org)
    execute_cmd(['rm', '-rf', '{0}/{1}-cli'.format(dot, org)])
    execute_cmd(['rm', '{0}/{1}'.format(prefix, org)])
    print('Removed {} command'.format(org))


def update(org):
    # check if there are any updates to the scripts repository
    check_install(org)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(dot, org), 'fetch']
    (out, err) = execute_cmd(update_cmd)
    if out:
        print("There are updates to the {0} command. To install them, run:\n".format(org))
        print("  groupthink --upgrade {0}".format(org))
    else:
        print("Your {0} command is already up to date.".format(org))


def upgrade(org):
    # upgrade organization scripts repository
    check_install(org)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(dot, org), 'pull']
    (out, err) = execute_cmd(update_cmd)
    if out.find('Already up-to-date'):
        print("Your {0} command is already up to date.".format(org))
    else:
        print('Upgraded {} command'.format(org))


def list_orgs():
    installed = installed_orgs()
    if installed:
        print("You have installed these scripts:\n")
        for org in installed:
            print("  - " + org.split('-')[0])
    else:
        print("You haven't installed any scripts. Install one with:\n")
        print("  groupthink --install <org>")


def installed_orgs():
    return [org for org in os.walk(dot).next()[1] if org.find('-cli') > 0]


def check_install(org, check_already=True):
    # check if org-cli repo already installed in ~/.groupthink
    installed = "{}-cli".format(org) in installed_orgs()
    if not installed and check_already:
        print("Error: {0} command not installed. You can try to install it with:\n".format(org))
        print("  groupthink --install {0}".format(org))
        sys.exit(1)
    elif installed and not check_already:
        print("Error: {0} command already installed. You can check for updates with:\n".format(org))
        print("  groupthink --update {0}".format(org))
        sys.exit(1)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main():
    parser = argparse.ArgumentParser(prog='groupthink', description="""Install a GitHub organization's CLI scripts. Given an 
        organization name, <org>, this package looks for and install the scripts contained in a repository with the name 
        <org>-cli.""")
    parser.add_argument('--install', '-i', action='store', dest='install', help="Provided a GitHub organization name, installs that organization's CLI scripts.")
    parser.add_argument('--uninstall', '-r', action='store', dest='uninstall', help="Removes an organization's CLI scripts.")
    parser.add_argument('--upgrade', '-c', action='store', dest='upgrade', help="Checks if there are updates to an organization's installed CLI scripts.")
    parser.add_argument('--update', '-u', action='store', dest='update', help="Updates an organization's installed CLI scripts.")
    parser.add_argument('--list', '-l', action='store_true', dest='list', help="Lists all organization CLI scripts you have installed.")
    args = parser.parse_args(sys.argv[1:])
    args_len = len([d for d in args.__dict__.values() if d])
    if args_len > 1:
        print("Error: Too many arguments provided")
        parser.print_help()
    elif args.install:
        install(args.install)
    elif args.list:
        list_orgs()
    elif args.uninstall:
        uninstall(args.uninstall)
    elif args.upgrade:
        upgrade(args.upgrade)
    elif args.update:
        update(args.update)
    elif not args_len:
        print("Error: You didn't provide any arguments")
        parser.print_help()
