# Import python libs
import re

def _check_perlbrew(ret, runas=None):
    '''
    Check to see if perlbrew is installed.
    '''
    if not __salt__['perlbrew.is_installed'](runas):
        ret['result'] = False
        ret['comment'] = 'Perlbrew is not installed.'
    return ret


def _check_and_install_perl(ret, perl, default=False, runas=None):
    '''
    Verify that perl is installed, install if unavailable
    '''
    ret = _check_perl(ret, perl, runas=runas)
    if not ret['result']:
        if __salt__['perlbrew.install_perl'](perl, runas=runas):
            ret['result'] = True
            ret['changes'][perl] = 'Installed'
            ret['comment'] = 'Successfully installed perl.'
            ret['default'] = False
        else:
            ret['result'] = False
            ret['comment'] = 'Could not install perl.'
            return ret

#    if default:
#        __salt__['perlbrew.set_default'](perl, runas=runas)

    return ret


def _check_perl(ret, perl, runas=None):
    '''
    Check that perl is installed
    '''
    match_version = True

#    match_micro_version = False
#    micro_version_regex = re.compile(r'-([0-9]{4}\.[0-9]{2}|p[0-9]+)$')
#    if micro_version_regex.search(perl):
#        match_micro_version = True

#    if re.search('^[a-z]+$', perl):
#        match_version = False
    perl = re.sub('^perl-', '', perl)

    for impl, version, default in __salt__['perlbrew.list'](runas=runas):
#        if impl != 'perl':
#            version = '{impl}-{version}'.format(impl=impl, version=version)
#        if not match_micro_version:
#            version = micro_version_regex.sub('', version)
#        if not match_version:
#            version = re.sub('-.*', '', version)
        if version == perl:
            ret['result'] = True
            ret['comment'] = 'Requested perl exists.'
            ret['default'] = default
            break
    return ret


def installed(name, default=False, runas=None):
    '''
    Verify that the specified perl is installed with Perlbrew. Perlbrew is
    installed when necessary.

    name
        The version of perl to install
    default : False
        Whether to make this perl the default.
    runas : None
        The user to run perlbrew as.
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    if __opts__['test']:
        ret['comment'] = 'Perl {0} is set to be installed'.format(name)
        return ret

    ret = _check_perlbrew(ret, runas)
    if ret['result'] == False:
        if not __salt__['perlbrew.install'](runas=runas):
            ret['comment'] = 'Perlbrew failed to install.'
            return ret
        else:
            return _check_and_install_perl(ret, name, default, runas=runas)
    else:
        return _check_and_install_perl(ret, name, default, runas=runas)

