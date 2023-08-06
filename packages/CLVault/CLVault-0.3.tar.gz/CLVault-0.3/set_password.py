#!/usr/bin/env python
from keyring import set_password
from getpass import getpass
import sys

def main(service, password=None):
    if password is None:
        password = getpass('Set your password: ')
    set_password(service, 'tarek', password)
    print('Password set.')

if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        print('Usage: %s service' % sys.executable)
        sys.exit(1)

    main(*sys.argv[1:])

