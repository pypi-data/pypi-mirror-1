#!/usr/bin/env python
#
# Setup script for the daily-notes
#
# Author: Ray Wang <wanglei1123@gmail.com>
#
# Usage: python setup.py install
#
# found classifiers at http://pypi.python.org/pypi?:action=list_classifiers

import os
from distutils.core import setup

version = '0.1.0'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read()

setup(
    name='daily-notes',
    version=version,
    description='This program is targeted to who will make some notes everyday.',
    long_description=long_description,
    license='GPLv3',
    author='Ray Wang',
    author_email='wanglei1123@gmail.com',
    url='http://code.google.com/p/daily-notes/',
    download_url='http://daily-notes.googlecode.com/files/',
    platforms="Python 2.5 and later.",
    # sorry, i am not a package.
    # packages=['daily-notes'],
    keywords=['pygtk', 'calendar'],
    namespace_packages=['daily-notes'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: X11 Applications :: GTK',
        'Framework :: IDLE',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Office/Business :: News/Diary']
    )
