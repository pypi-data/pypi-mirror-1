#!/usr/bin/env python
# vim:et:sw=4:ts=4

pkg_info_text = """
Metadata-Version: 1.1
Name: python-commons
Version: 0.1
Author: Yang Zhang
Author-email: yaaang NOSPAM at REMOVECAPS gmail
Home-page: http://assorted.sourceforge.net/python-commons
Download-url: http://assorted.sourceforge.net/python-commons/download
Summary: Python Commons
License: Python Software Foundation License
Description: General-purpose library of utilities and extensions to the
        standard library.
Keywords: Python,common,commons,utility,utilities,library,libraries
Platform: any
Provides: commons
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: No Input/Output (Daemon)
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: Python Software Foundation License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Topic :: Communications
Classifier: Topic :: Database
Classifier: Topic :: Internet
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Topic :: System
Classifier: Topic :: System :: Filesystems
Classifier: Topic :: System :: Logging
Classifier: Topic :: System :: Networking
Classifier: Topic :: Text Processing
Classifier: Topic :: Utilities
"""

list_keys = set( [ 'Classifier' ] )
pkg_info = {}
for line in pkg_info_text.split( '\n' ):
    if line.strip() != '':
        if line.startswith( ' '*8 ):
            pkg_info[ key ] += line[ 7 : ]
        else:
            key, value = line.split( ': ', 1 )
            if key in list_keys:
                try:
                    pkg_info[ key ].append( value )
                except:
                    pkg_info[ key ] = [ value ]
            else:
                pkg_info[ key ] = value

arg_keys = """
name
version
author
author_email
description: Summary
download_url: Download-url
long_description: Description
keywords: Keywords
url: Home-page
license
classifiers: Classifier
platforms: Platform
"""

args_nontranslations = set()
args_translations = {}
for line in arg_keys.split( '\n' ):
    if line.strip() != '':
        splitted = line.split( ': ', 1 )
        dest_name = splitted[ 0 ]
        if len( splitted ) == 2:
            source_name = splitted[ 1 ]
            args_translations[ source_name ] = dest_name
        else:
            args_nontranslations.add( dest_name )

args = {}
for key, value in pkg_info.iteritems():
    dest_name = None
    try:
        dest_name = args_translations[ key ]
    except KeyError:
        key = key.lower().replace('-','_')
        if key in args_nontranslations:
            dest_name = key
    if dest_name is not None:
        args[ dest_name ] = value

import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 3):
    from distutils.core import setup
    _setup = setup
    def setup(**kwargs):
        for key in [
            # distutils >= Python 2.3 args
            # XXX probably download_url came in earlier than 2.3
            "classifiers", "download_url",
            # setuptools args
            "install_requires", "zip_safe", "test_suite",
            ]:
            if kwargs.has_key(key):
                del kwargs[key]
        # Only want packages keyword if this is a package,
        # only want py_modules keyword if this is a single-file module,
        # so get rid of packages or py_modules keyword as appropriate.
        if kwargs["packages"] is None:
            del kwargs["packages"]
        else:
            del kwargs["py_modules"]
        apply(_setup, (), kwargs)
else:
    from setuptools import setup, find_packages

setup(
#    scripts = ['frontend/py_hotshot.py'],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    zip_safe = True,
    **args
)
