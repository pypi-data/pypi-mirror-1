# -*- encoding: utf-8 -*-
from setuptools import setup

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

setup(name='CLVault',
      version='0.5',
      description="Command-Line utility to store and retrieve passwords",
      url="http://bitbucket.org/tarek/clvault",
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      packages=['clvault'],
      entry_points={'console_scripts': [
                      'clvault-get = clvault.get_password:main',
                      'clvault-set = clvault.set_password:main',
                      'clvault-list = clvault.passwordlist:get_services']},
      install_requires=['keyring'],
      long_description=README,
      license='PSF',
      keywords=['keyring', 'password', 'crypt']
    )

