#!/usr/bin/env python
from distutils.core import setup
from sys import version

trove = filter(bool, """
Development Status :: 3 - Alpha
Environment :: Other Environment
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python
""".splitlines())

if version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='pynis',
    version='0.1',
    description='Python NIS utilitiy',
    author='Ludvig Ericson',
    author_email='ludvig.ericson@gmail.com',
    url='http://lericson.se/',
    packages=['pynis'],
    classifiers=trove
)
