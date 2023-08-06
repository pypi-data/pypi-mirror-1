import os
from ConfigParser import ConfigParser

# propose that expanduser takes several params
_SERVICE_CFG = os.path.expanduser(os.path.join('~', '.clvault'))

def get_services():
    config = ConfigParser()
    if os.path.exists(_SERVICE_CFG):
        config.read(_SERVICE_CFG)
    else:
        print('No password saved.')
        return

    print('Registered services:')
    for service, description in config.items('clvault'):
        print('\t%s\t%s' % (service, description))

def add_service(name, description):
    config = ConfigParser()
    if os.path.exists(_SERVICE_CFG):
        config.read(_SERVICE_CFG)
    if not config.has_section('clvault'):
        config.add_section('clvault')
    config.set('clvault', name, description)
    config.write(open(_SERVICE_CFG, 'w'))

