#!/usr/bin/env python

from distutils.core import setup

setup(name='PathTo',
      version='0.3.0',
      description='Resource-oriented client APIs generated dynamically from auto-discovered, or locally-configured metadata',
      author='Michael Burrows',
      author_email='mjb@asplake.co.uk',
      url='http://bitbucket.org/asplake/path_to',
      py_modules=['path_to'],
      requires=["httplib2(>=0.6.0)", "DescribedRoutes(>=0.2.2)", "LinkHeader(>=0.2.0)"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
