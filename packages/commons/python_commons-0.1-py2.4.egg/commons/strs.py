# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
String formatting.
"""

import itertools

def format( *args ):
    """Formats the args as they would be by the C{print} built-in."""
    return ' '.join( itertools.imap( str, args ) )

def safe_ascii( s ):
    """Casts a Unicode string to a regular ASCCII string. This may be
    lossy."""
    if isinstance( s, unicode ) and s == str( s ):
        return str( s )
    else:
        return s
