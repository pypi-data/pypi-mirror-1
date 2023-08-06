# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'troll.storage'
version = '0.4'
readme = open("README.txt").read()

setup(name = name,
      version = version,
      description = 'Troll abstract storage layer',
      long_description = readme[readme.find('\n\n'):],
      keywords = 'zope grok storage',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://tracker.trollfot.org/',
      download_url = 'http://pypi.python.org/pypi/troll.storage',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['troll'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = True,
      test_suite = 'troll.storage.tests',
      install_requires=[
          'setuptools',
          'five.grok'
      ],
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
