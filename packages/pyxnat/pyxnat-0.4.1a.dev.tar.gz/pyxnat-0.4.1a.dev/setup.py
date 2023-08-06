#!/usr/bin/env python

from distutils.core import setup
import sys

import pyxnat


# For some commands, use setuptools
if len(set(('develop', 'sdist', 'release', 'bdist_egg', 'bdist_rpm',
           'bdist', 'bdist_dumb', 'bdist_wininst', 'install_egg_info',
           'build_sphinx', 'egg_info', 'easy_install', 'upload',
            )).intersection(sys.argv)) > 0:
    from setupegg import extra_setuptools_args

# extra_setuptools_args is injected by the setupegg.py script, for
# running the setup with setuptools.
if not 'extra_setuptools_args' in globals():
    extra_setuptools_args = dict()


setup(name='pyxnat',
      version=pyxnat.__version__,
      summary='Xnat in Python',
      author='Yannick Schwartz',
      author_email='yannick.schwartz@cea.fr',
#      url='https://launchpad.net/pyxnat',
      packages = ['pyxnat'],
      package_data={'pyxnat': ['externals/*.py', 'tools/*', 'test/*',
                               'externals/joblib/*.py', 
                               'externals/simplejson/*.py',
                               '*.py', '*.cfg'
                              ]
                   },
      description="""Xnat in Python""",
      long_description=pyxnat.__doc__,
      license='BSD',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities',
      ],

      platforms='any',
      **extra_setuptools_args)

