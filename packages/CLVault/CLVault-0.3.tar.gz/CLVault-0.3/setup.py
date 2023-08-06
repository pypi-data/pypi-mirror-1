# -*- encoding: utf-8 -*-
from distutils.core import setup

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

setup(name='CLVault',
      version='0.3',
      description="Command-Line utility to store and retrieve passwords",
      url="http://bitbucket.org/tarek/clvault",
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      scripts=['get_password.py', 'set_password.py'],
      long_description=README,
      license='PSF',
      keywords=['keyring', 'password', 'crypt']
    )

