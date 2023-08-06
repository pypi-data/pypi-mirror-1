# -*- encoding: utf-8 -*-
from distutils.core import setup

setup(name='CLVault',
      version='0.1',
      description="Command-Line utility to store and retrieve passwords",
      url="http://bitbucket.org/tarek/clvault",
      author=u"Tarek Ziadé",
      author_email="tarek@ziade.org",
      scripts=['get_password.py', 'set_password.py'],
    )

