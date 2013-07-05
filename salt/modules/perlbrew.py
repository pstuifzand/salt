'''
Manage perl installations and gemsets with Perlbrew, the Ruby Version Manager.
'''

# Import python libs
import re
import os

__opts__ = {
    'perlbrew.runas': None,
}

def _get_perlbrew_location(runas=None):
    if runas:
        perlbrewpath = '~{0}/perl5/perlbrew/bin/perlbrew'.format(runas)
        return os.path.expanduser(perlbrewpath)
    return '/usr/local/bin/perlbrew'

def _perlbrew(command, arguments='', runas=None):
    if not runas:
        runas = __salt__['config.option']('perlbrew.runas')
    if not is_installed(runas):
        return False

    ret = __salt__['cmd.run_all'](
        '{perlbrewpath} {command} {arguments}'.
        format(perlbrewpath=_get_perlbrew_location(runas), command=command, arguments=arguments),
        runas=runas)
    if ret['retcode'] == 0:
        return ret['stdout']
    else:
        return False


def _perlbrew_do(perl, command, runas=None):
    return _perlbrew('exec --with={perl} {command}'.
                format(perl=perl, command=command),
                runas=runas)


def is_installed(runas=None):
    '''
    Check if Perlbrew is installed.
    
    CLI Example::

        salt '*' perlbrew.is_installed
    '''
    return __salt__['cmd.has_exec'](_get_perlbrew_location(runas))


def install(runas=None):
    '''
    Install Perlbrew system wide.

    CLI Example::

        salt '*' perlbrew.install
    '''
    # Perlbrew dependencies on Ubuntu 10.04:
    #   bash coreutils gzip bzip2 gawk sed curl git-core subversion
    installer = 'http://install.perlbrew.pl'
    return 0 == __salt__['cmd.retcode'](
        # the Perlbrew installer automatically does a multi-user install when it is invoked with root privileges
        'curl -s -L {installer} | bash'.format(installer=installer), runas=runas)


def install_perl(perl, runas=None):
    '''
    Install a perl implementation.

    perl
        The version of perl to install.
    runas : None
        The user to run perlbrew as.

    CLI Example::

        salt '*' perlbrew.install_perl 5.14.2
    '''
    # MRI/RBX/REE dependencies for Ubuntu 10.04:
    #   build-essential openssl libreadline6 libreadline6-dev curl
    #   git-core zlib1g zlib1g-dev libssl-dev libyaml-dev libsqlite3-0
    #   libsqlite3-dev sqlite3 libxml2-dev libxslt1-dev autoconf libc6-dev
    #   libncurses5-dev automake libtool bison subversion perl
    return _perlbrew('install', perl, runas=runas)


def reinstall_perl(perl, runas=None):
    '''
    Reinstall a perl implementation.

    perl
        The version of perl to reinstall.
    runas : None
        The user to run perlbrew as.

    CLI Example::

        salt '*' perlbrew.reinstall_perl 5.14.2
    '''
    return _perlbrew('reinstall', perl, runas=runas)


def list(runas=None):
    '''
    List all perlbrew installed perls.

    runas : None
        The user to run perlbrew as.

    CLI Example::

        salt '*' perlbrew.list
    '''
    perls = []

    for line in _perlbrew('list', '', runas=runas).splitlines():
        match = re.match(r'^([*> ]) ([^- ]+)-([^ ]+)', line)
        if match:
            perls.append([
                match.group(2), match.group(3), match.group(1) == '*'
            ])
    return perls

def do(perl, command, runas=None):  # pylint: disable-msg=C0103
    '''
    Execute a command in an Perlbrew controlled environment.

    perl:
        The perl to use.
    command:
        The command to execute.
    runas : None
        The user to run perlbrew as.

    CLI Example::

        salt '*' perlbrew.exec 2.0.0 <command>
    '''
    return _perlbrew_do(perl, command, runas=runas)

def install_cpanm(runas=None):  # pylint: disable-msg=C0103
    '''
    Execute a command in an Perlbrew controlled environment.

    perl:
        The perl to use.
    command:
        The command to execute.
    runas : None
        The user to run perlbrew as.

    CLI Example::

        salt '*' perlbrew.install_cpanm
    '''
    return _perlbrew('install-cpanm', '', runas=runas)

