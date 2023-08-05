##########################################################################
# haufe.selenium - a wrapper for the Selenium remote server
#
# (C) Haufe Mediengruppe, Freiburg, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Environment :: Web Environment',
]

version = open('version.txt').read().strip()
desc = open('README.txt').read().strip()
changes = open('CHANGES.txt').read().strip()

long_description = desc + '\n\n\nChanges:\n========\n\n' + changes

setup(name='haufe.selenium',
      version=version,
      license='LGPL 2.1',
      author='Andreas Jung',
      author_email='list@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='list@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://pypi.python.org/pypi/haufe.selenium',
      description='A Python wrapper for controlling the Selenium Remote Server',
      long_description=long_description,
      packages=['haufe', 'haufe.selenium'],
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['haufe'],
      entry_points={'console_scripts' : ['selsrvctl= haufe.selenium.cli:main',
                                        ]},
      requires=['zdaemon'],
      )


