# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Sequences, streams, and generators.

@var default_chunk_size: The default chunk size used by L{chunkify}.
"""

default_chunk_size = 4096

def chunkify( stream, chunk_size = default_chunk_size ):
    """
    Given an input stream (an object exposing a file-like interface),
    reads data in from it one chunk at a time. This is a generator
    which yields those chunks as they come.

    @param stream: The input stream.
    @type stream: stream

    @param chunk_size: The size of the chunk (usually the number of
    bytes to read).
    @type chunk_size: int
    """
    offset = 0
    while True:
        chunk = stream.read( chunk_size )
        if not chunk:
            break
        yield offset, chunk
        offset += len( chunk )

def total( iterable ):
    """
    Counts the number of items in an iterable. Note that this will
    consume the elements of the iterable, and if the iterable is
    infinite, this will not halt.

    @param iterable: The iterable to count.
    @type iterable

    @return: The number of elements consumed.
    @rtype: int
    """
    return sum( 1 for i in iterable )
