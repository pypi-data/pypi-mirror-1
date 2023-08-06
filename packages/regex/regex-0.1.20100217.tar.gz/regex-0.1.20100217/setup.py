#!/usr/bin/env python

import os
import shutil
import sys

from distutils.core import setup, Extension

MAJOR, MINOR = sys.version_info[:2]
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

if (MAJOR, MINOR) == (2, 6):
    shutil.copy(os.path.join(SRC_DIR, 'Python26', 'unicodedata_db.h'), 
    		SRC_DIR)
elif (MAJOR, MINOR) == (2, 5):
    shutil.copy(os.path.join(SRC_DIR, 'Python25', 'unicodedata_db.h'), 
                SRC_DIR)
else:
    print "WARNING: No unicodedata_db.h prepared." 

setup(
    name='regex',
    version='0.1.20100217',
    description='Alternate regular expression module, to replace re.',
    long_description=open(os.path.join(SRC_DIR, 'Features.txt')).read(),
    author='Matthew Barnett',
    author_email='regex@mrabarnett.plus.com',
    # PyPI appears to overwrite author field with maintainer field
    # avoid apparent plagarism for now.
    #maintainer='Alex Willmer',
    #maintainer_email='alex@moreati.org.uk',
    url='http://bugs.python.org/issue2636',
    classifiers=[
        'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: Python Software Foundation License',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: Information Analysis',
	'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
	'Topic :: Text Processing :: General',
	],
    license='Python Software Foundation License',

    py_modules = ['regex'],
    ext_modules=[Extension('_regex', ['_regex.c'])],
    )
