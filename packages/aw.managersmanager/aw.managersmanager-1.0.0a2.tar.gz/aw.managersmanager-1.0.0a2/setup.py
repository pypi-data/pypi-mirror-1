# -*- coding: utf-8 -*-
# $Id$

from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('aw', 'managersmanager', 'version.txt')

setup(name='aw.managersmanager',
      version=version,
      description="Manages Plone site managers on multiple sites and clusters.",
      long_description=(_textFromPath("README.txt") + "\n\n" +
                        _textFromPath("docs", "HISTORY.txt")),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Environment :: Console",
          "Programming Language :: Python",
          "Development Status :: 3 - Alpha"
          ],
      keywords='plone managers console',
      author='Alter Way Solutions',
      author_email='support@ingeniweb.com',
      url='http://pypi.python.org/pypi/aw.managersmanager',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['aw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          ],
      entry_points={
          'console_scripts': ['plonemanagers = aw.managersmanager.console:main']
          },
      )
