#!/usr/bin/env python

from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


setup(name='rnc2rng',
      version='1.0',
      description='Converts from RelaxNG Compact Syntax to RelaxNG XML Syntax',
      author='David Mertz',
      author_email='mertz@gnosis.cx',
      url='http://www.gnosis.cx/download/relax/',
      maintainer="Hartmut Goebel",
      maintainer_email="h.goebel@goebel-consult.de",
      packages=['rnc2rng'],
      scripts=['scripts/rnc2rng'],
      classifiers = ['Development Status :: 5 - Production/Stable',
                    'Environment :: Console',
                    'Intended Audience :: Developers',
                    'Intended Audience :: System Administrators',
                    'License :: Public Domain',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Text Processing :: Markup :: XML',
                    'Topic :: Utilities',
                    ]
     )

