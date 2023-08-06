#!/usr/bin/env python

import sys
if sys.version_info < (2, 3):
  print>>sys.stderr, "You need Python 2.3 or higher to use OpenKremlin."
  sys.exit(1)

try:
  from setuptools import setup
  setuptools = True
except ImportError:
  print>>sys.stderr, "Warning: can't import setuptools; falling back to distutils"
  from distutils.core import setup
  setuptools = False

args = dict(
    name='openkremlin',
    version='0.2',
    install_requires=['pycrypto>=2.0.1'],

    packages=['openkremlin'],
    scripts=['unkgb'],
    data_files=[],

    author='nonguru',
    author_email='thenonguru@gmail.com',
    description='Free program to decrypt .kgb archives',
    license='MIT',
    keywords='kremlin encrypt cryptography kgb',
    url='http://sharesource.org/project/openkremlin/',
    
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'License :: OSI Approved :: MIT License',
      'Topic :: Security :: Cryptography'])

try:
  import py2exe
  args['console'] = [{'script': 'unkgb.py',
                      'icon_resources': [(1, 'openkremlin.ico')],
                      }]
except ImportError:
  py2exe = None

setup(**args)

