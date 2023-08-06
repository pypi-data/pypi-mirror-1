# -*- encoding: utf-8 -*-
from distutils.core import setup

with open('README.txt') as f:
    README = f.read()

setup(name='CLVault',
      version='0.2',
      description="Command-Line utility to store and retrieve passwords",
      url="http://bitbucket.org/tarek/clvault",
      author=u"Tarek Ziadé",
      author_email="tarek@ziade.org",
      scripts=['get_password.py', 'set_password.py'],
      long_description=README
    )

