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

cp1252_to_unicode_translations = [ (u'\x80',u'\u20AC'),
                                   (u'\x82',u'\u201A'),
                                   (u'\x83',u'\u0192'),
                                   (u'\x84',u'\u201E'),
                                   (u'\x85',u'\u2026'),
                                   (u'\x86',u'\u2020'),
                                   (u'\x87',u'\u2021'),
                                   (u'\x88',u'\u02C6'),
                                   (u'\x89',u'\u2030'),
                                   (u'\x8A',u'\u0160'),
                                   (u'\x8B',u'\u2039'),
                                   (u'\x8C',u'\u0152'),
                                   (u'\x8E',u'\u017D'),
                                   (u'\x91',u'\u2018'),
                                   (u'\x92',u'\u2019'),
                                   (u'\x93',u'\u201C'),
                                   (u'\x94',u'\u201D'),
                                   (u'\x95',u'\u2022'),
                                   (u'\x96',u'\u2013'),
                                   (u'\x97',u'\u2014'),
                                   (u'\x98',u'\u02DC'),
                                   (u'\x99',u'\u2122'),
                                   (u'\x9A',u'\u0161'),
                                   (u'\x9B',u'\u203A'),
                                   (u'\x9C',u'\u0153'),
                                   (u'\x9E',u'\u017E'),
                                   (u'\x9F',u'\u0178') ]

def cp1252_to_unicode(x):
    """Converts characters 0x80 through 0x9f to their proper Unicode
    equivalents.  See
    U{http://www.intertwingly.net/stories/2004/04/14/i18n.html} for the nice
    translation table on which this is based."""
    for a,b in cp1252_to_unicode_translations:
        x = x.replace(a,b)
    return x

