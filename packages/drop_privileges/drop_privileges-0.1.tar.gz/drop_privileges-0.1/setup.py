#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='drop_privileges',
    version='0.1',
    description='Drop root privileges on a POSIX system.',
    author='Gavin Baker, Hartmut Goebel',
    author_email='h.goebel@goebel-consult.de',
    #url='http://forschung.goebel-consult.de/misc/net-status-monitor/',
    py_modules=['drop_privileges'],
    license='MIT License',
     classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
       )

