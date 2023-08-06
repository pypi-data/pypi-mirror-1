#!/usr/bin/python
#
# $Id$

from distutils.core import setup

classifiers="""\
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved :: Python Software Foundation License
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Communications
Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries"""

setup(name='shortie',
    description='python library for the short.ie api',
    author='Niall Sheridan',
    author_email='nsheridan@gmail.com',
    url='http://www.evil.ie/projects/python/shortie',
    license='Python',
    long_description='python library for the short.ie api',
    platforms='Any',
    version='0.2',
    package_dir={'shortie': ''},
    packages=['shortie'],
    classifiers=classifiers.split('\n')
    )

