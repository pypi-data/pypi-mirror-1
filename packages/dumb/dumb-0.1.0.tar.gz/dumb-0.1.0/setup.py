#!/usr/bin/env python

from distutils.core import setup
setup(name='dumb',
      version='0.1.0',
      description='Distributed Unified Mangler of Bookmarks',
      author='Elena "of Valhalla" Grandi',
      author_email='elena.valhalla@gmail.com',
      url='http://dumb.grys.it',
      download_url='http://dumb.grys.it/_downloads/dumb-0.1.0.tar.gz',
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
          ],
      package_dir = {'': 'lib'},
      py_modules = ['dumb'],
      scripts=['scripts/dumb-add','scripts/dumb-get-command']
      )

