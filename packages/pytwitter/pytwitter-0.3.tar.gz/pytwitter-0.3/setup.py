#!/usr/bin/python
#
# $Id: setup.py 175 2009-05-10 00:29:23Z nsheridan@EVIL.IE $

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

setup(name='pytwitter',
    description='python library for the twitter api',
    author='Niall Sheridan',
    author_email='nsheridan@gmail.com',
    url='http://www.evil.ie/projects/python/pytwitter',
    license='Python',
    long_description='python library for the twitter api',
    platforms='Any',
    version='0.3',
    package_dir={'pytwitter': ''},
    packages=['pytwitter'],
    classifiers=classifiers.split('\n')
    )
