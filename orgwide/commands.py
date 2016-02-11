import subprocess
import os
import sys

prefix = '/usr/local/bin'

def install(org):
    # install organization scripts repository and create orgwide script
    print('Installing {} command'.format(org))
    install_repo = ['git', 'clone', 'https://github.com/{0}/{1}-cli/'.format(org, org), prefix + '/{}-cli'.format(org)]
    (out, err) = execute_cmd(install_repo)
    scripts_dir = os.getcwd() + '/orgwide/scripts'
    install_script = ['cp', '-p', '{}/orgwide-script'.format(scripts_dir), '{0}/{1}'.format(prefix, org)]
    (out, err) = execute_cmd(install_script)


def update(org):
    # update organization scripts repository
    print('Updating {} command'.format(org))
    update_cmd = ['git', '--git-dir={0}/{1}-cli/.git'.format(prefix, org), 'pull']
    (out, err) = execute_cmd(update_cmd)


def list_orgs(org):
    # list all organization scripts
    # TO DO: autocomplete from list
    print('You can install scripts from these organizations')


def clean(org):
    # remome organization scripts repo and orgwide script
    print('Removing {} command'.format(org))
    clean_repo = ['rm', '-rf', '{0}/{1}-cli'.format(prefix, org)]
    (out, err) = execute_cmd(clean_repo)
    clean_script = ['rm', '{0}/{1}'.format(prefix, org)]
    (out, err) = execute_cmd(clean_script)

def organizations():
    pass


def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()

def main():
    args=sys.argv
    args.pop(0)
    # try:
    if args[0] == 'install':
        install(args[1])
    elif args[0] == 'update':
        update(args[1])
    elif args[0] == 'list':
        list_orgs()
    elif args[0] == 'clean':
        clean(args[1])
    # except:
    #     print('Invalid command')
