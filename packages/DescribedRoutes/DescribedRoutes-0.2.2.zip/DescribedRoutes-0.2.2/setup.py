#!/usr/bin/env python

from distutils.core import setup

setup(name='DescribedRoutes',
      version='0.2.2',
      description='Dynamic, framework-neutral metadata describing path/URI '
                   'structures natively in Python and through JSON and YAML '
                   'representations.',
      author='Michael Burrows',
      author_email='mjb@asplake.co.uk',
      url='http://bitbucket.org/asplake/described_routes',
      packages=['described_routes', 'tests'],
      requires=["LinkHeader(>=0.2.0)"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
