# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
File and directory manipulation.

@var invalid_filename_chars: The characters which are usually
prohibited on most modern file systems.

@var invalid_filename_chars_regex: A regex character class constructed
from L{invalid_filename_chars}.
"""

import os, re, tempfile

def soft_makedirs( path ):
    """
    Emulate C{mkdir -p} (doesn't complain if it already exists).

    @param path: The path of the directory to create.
    @type path: str

    @raise OSError: If it cannot create the directory. It only
    swallows OS error 17.
    """
    try:
        os.makedirs( path )
    except OSError, ex:
        if ex.errno == 17:
            pass
        else:
            raise

def temp_dir( base_dir_name, do_create_subdir = True ):
    """
    Get a temporary directory without polluting top-level /tmp. This follows
    Ubuntu's conventions, choosing a temporary directory name based on
    the given name plus the user name to avoid user conflicts.

    @param base_dir_name: The "name" of the temporary directory. This
    is usually identifies the purpose of the directory, or the
    application to which the temporary directory belongs. E.g., if joe
    calls passes in C{"ssh-agent"} on a standard Linux/Unix system,
    then the full path of the temporary directory will be
    C{"/tmp/ssh-agent-joe"}.
    @type base_dir_name: str

    @param do_create_subdir: If C{True}, then creates a
    sub-sub-directory within the temporary sub-directory (and returns
    the path to that). The sub-sub-directory's name is randomized
    (uses L{tempfile.mkdtemp}).
    @type do_create_subdir: bool

    @return: The path to the temporary (sub-)sub-directory.
    @rtype: str
    """
    base_dir_name += '-' + os.environ[ 'USER' ]
    base_dir = paths.path( tempfile.gettempdir() ) / base_dir_name
    soft_makedirs( base_dir )
    if do_create_subdir:
        return tempfile.mkdtemp( dir = base_dir )
    else:
        return base_dir

invalid_filename_chars = r'*|\/:<>?'
invalid_filename_chars_regex = r'[*|\\\/:<>?]'

def cleanse_filename( filename ):
    """
    Replaces all problematic characters in a filename with C{"_"}, as
    specified by L{invalid_filename_chars}.

    @param filename: The filename to cleanse.
    @type filename: str
    """
    pattern = invalid_filename_chars_regex
    return re.sub( pattern, '_', filename )

