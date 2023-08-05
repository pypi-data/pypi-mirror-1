#!/usr/bin/env python
"""
Distutils setup script for pyhjb
"""

from os import getcwd, listdir
from os.path import join as join_path, isfile, walk
import re

import hjb

hjb_path = getcwd()
# Use setup tools if its available
try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
except:
    from distutils.core import setup

def relative_path(base, name):
    if not name.startswith(base):
        return name
    else:
        return name[len(base):]

def make_sample_files():
    def list_sample_files(acc, dirname, fnames):
        [acc.append('samples' + relative_path(sample_base, join_path(dirname, f))) 
            for f in fnames
            if isfile(join_path(dirname, f))]
    sample_files = []
    walk(join_path(hjb_path, 'samples'), list_sample_files, sample_files)
    return sample_files

version = str(hjb.__version__)
(author, author_email) = re.match('^(.*?)\s*<(.*)>$', hjb.__author__).groups()
url = hjb.__url__
license = hjb.__license__
sample_base = join_path(hjb_path, 'samples') 

setup(name = "pyhjb",
      version = version,
      description = "Python HJB (HTTP JMS Bridge) client library",
      author = author,
      author_email = author_email,
      url = url,
      license = license,
      entry_points = {
          'console_scripts' : [
              'hjbactivemq = hjb.scripts.hjbactivemq:main',
              'hjbwsmq = hjb.scripts.hjbwsmq:main',
              'hjbjboss = hjb.scripts.hjbjboss:main',
              'hjbswiftmq = hjb.scripts.hjbswiftmq:main',
              'make_jboss_destinations = hjb.scripts.make_jboss_destinations:main'
          ]
      },
      packages = ["hjb", "hjb.test", "hjb.scripts"],
      package_data = {"hjb": make_sample_files()},
      zip_safe=False,
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP',
          'Environment :: Console',
          'Environment :: Web Environment',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
      ],
      keywords = "HJB JMS java messaging MQ queue topic HTTP",
      long_description = """

  PyHJB is a python client library for accessing JMS 1.1 (Java Message Service)
  messaging providers via HJB, the HTTP JMS bridge.

  `HJB <http://hjb.berlios.de>`_ provides access to JMS resources via HTTP.  It
  acts as an HTTP gateway server for any JMS messaging provider, and provides a
  RESTful equivalent for most of the non-optional portions of the JMS API. 

  PyHJB is a pure python package which, via HJB, allows python programs to:

  * send/receive messages from **any** Enterprise Messaging System that
    supports JMS.  It is distributed with a few demo scripts showing it being
    used with a selection of well-known messaging providers: WebSphere MQ,
    Swift MQ, Active MQ and JBoss Messaging.

  * register JMS administrable objects via JMS, e.g, queues, topics and
    connection factories.

  * configure JMS runtime objects, e.g, connections, sessions, message
    consumers, message producers, queue browsers and durable subscribers etc.

  Importantly, python programs written using PyHJB are portable across JMS
  messaging providers.  The programs use the JMS API via HTTP rather than a
  vendor's custom messaging API, and thus combine two important maintainability
  traits:

  * the use of the JMS API

  * being written in python!

"""
    )
