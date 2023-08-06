#!/usr/bin/env python
from keyring import set_password
from getpass import getpass
import sys

from clvault.passwordlist import add_service

def _main(service, password=None):
    if password is None:
        password = getpass('Set your password: ')
    username = raw_input('Set the associated username (can be blank): ')
    username = username.strip()
    if username != '':
        password = '%s:::%s' % (username, password)
    description = raw_input('Set a description (can be blank): ')
    description = description.strip()
    add_service(service, description)
    set_password(service, 'clvault-password', password)
    print('Password set.')

def main():
    if len(sys.argv) not in (2, 3):
        print('Usage: clvault-set service')
        sys.exit(1)

    _main(*sys.argv[1:])


if __name__ == '__main__':
    main()

