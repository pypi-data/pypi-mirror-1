#!/usr/bin/env python
from keyring import set_password
import sys

def main(service, password):
    set_password(service, 'tarek', password)
    print('Password set.')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s service password' % sys.executable)
        sys.exit(1)

    main(*sys.argv[1:])

