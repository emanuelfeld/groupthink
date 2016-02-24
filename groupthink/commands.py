import subprocess
import os
import sys
import argparse
from glob import glob

prefix = '/usr/local/bin'
home = os.path.expanduser('~')
dot = '{}/.groupthink'.format(home)


def install(org, out=sys.stdout, prefix=prefix, dot=dot):
    # install organization scripts repository in ~/.groupthink
    # and add groupthink script to /usr/local/bin
    check_install(org, check_already=False, prefix=prefix, dot=dot)
    try:
        execute_cmd(['mkdir', '-p', dot])
        repo_url = 'https://github.com/{0}/{0}-cli.git'.format(org)
        repo_dest = '{}/{}-cli'.format(dot, org)
        (msg, err) = execute_cmd(['git', 'clone', repo_url, repo_dest])
        if err.find('fatal: ') > -1:
            sys.exit(1)
        groupthink_script = os.path.dirname(os.path.realpath(__file__)) + '/scripts/groupthink-script'
        groupthink_dest = '{}/{}'.format(prefix, org)
        execute_cmd(['rm', groupthink_dest])
        execute_cmd(['cp', '-p', groupthink_script, groupthink_dest])
        out.write('Installed {} command.\n'.format(org))
    except:
        out.write("Could not get {0}-cli command. Please make sure https://github.com/{0}/{0}-cli exists.\n".format(org))


def uninstall(org, out=sys.stdout, prefix=prefix, dot=dot):
    # remove organization scripts repo and groupthink script
    check_install(org, check_already=True, prefix=prefix, dot=dot)
    execute_cmd(['rm', '-rf', '{0}/{1}-cli'.format(dot, org)])
    execute_cmd(['rm', '{0}/{1}'.format(prefix, org)])
    out.write('Removed {} command.\n'.format(org))


def update(org, out=sys.stdout, prefix=prefix, dot=dot):
    # check if there are any updates to the scripts repository
    check_install(org, check_already=True, prefix=prefix, dot=dot)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(dot, org), 'fetch']
    (msg, err) = execute_cmd(update_cmd)
    if msg:
        out.write("There are updates to the {0} command. To install them, run:\n".format(org))
        out.write("  groupthink --upgrade {0}\n".format(org))
    else:
        out.write("Your {0} command is already up to date.\n".format(org))


def upgrade(org, out=sys.stdout, prefix=prefix, dot=dot):
    # upgrade organization scripts repository
    check_install(org, check_already=True, prefix=prefix, dot=dot)
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(dot, org), 'pull']
    (msg, err) = execute_cmd(update_cmd)
    if msg.find('Already up-to-date') > -1:
        out.write("Your {0} command is already up to date.\n".format(org))
    else:
        out.write('Upgraded {} command.\n'.format(org))


def list_orgs(out=sys.stdout, prefix=prefix, dot=dot):
    # print out a list of organizations whose scripts have been
    # installed to ~/.groupthink
    installed = installed_orgs(dot)
    if installed:
        out.write("You have installed these scripts:\n")
        for org in installed:
            out.write("  - {}\n".format(org))
    else:
        out.write("You haven't installed any scripts. Install one with:\n")
        out.write("  groupthink --install <org>\n")


def installed_orgs(dot=dot):
    # return a list of organization whose scripts have been installed
    # to ~/.groupthink
    installed = []
    for org in glob('{}/*/'.format(dot)):
        org_name = org.rstrip('/').split('/')[-1]
        if org_name.find('-cli') > 0:
            installed.append(org_name.split('-cli')[0])
    return installed


def check_install(org, check_already=True, out=sys.stdout, prefix=prefix, dot=dot):
    # check if org-cli repo already installed in ~/.groupthink
    installed = any(installed_orgs(dot))
    if not installed and check_already:
        out.write("Error: {0} command not installed. You can try to install it with:\n".format(org))
        out.write("  groupthink --install {0}\n".format(org))
        sys.exit(0)
    elif installed and not check_already:
        out.write("Error: {0} command already installed. You can check for updates with:\n".format(org))
        out.write("  groupthink --update {0}\n".format(org))
        sys.exit(0)


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def main(argv=sys.argv, out=sys.stdout):
    parser = argparse.ArgumentParser(prog='groupthink', description="""Install a GitHub organization's CLI scripts. Given an 
        organization name, <org>, this package looks for and install the scripts contained in a repository with the name 
        <org>-cli.""")
    parser.add_argument('--install', '-i', action='store', dest='install', help="Provided a GitHub organization name, installs that organization's CLI scripts.")
    parser.add_argument('--uninstall', '-r', action='store', dest='uninstall', help="Removes an organization's CLI scripts.")
    parser.add_argument('--upgrade', '-c', action='store', dest='upgrade', help="Checks if there are updates to an organization's installed CLI scripts.")
    parser.add_argument('--update', '-u', action='store', dest='update', help="Updates an organization's installed CLI scripts.")
    parser.add_argument('--list', '-l', action='store_true', dest='list', help="Lists all organization CLI scripts you have installed.")
    args = parser.parse_args(argv[1:])
    args_len = len([d for d in args.__dict__.values() if d])
    if args_len > 1:
        out.write("Error: Too many arguments provided\n")
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
        out.write("Error: You didn't provide any arguments\n")
        parser.print_help()
