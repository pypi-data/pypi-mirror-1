# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

from contextlib import *
from time import *

"""
Miscellanea.
"""

def generate_bit_fields(count):
    """
    A generator of [2^i] for i from 0 to (count - 1). Useful for,
    e.g., enumerating bitmask flags::

        red, yellow, green, blue = generate_bit_fields(4)
        color1 = blue
        color2 = red | yellow

    @param count: The number of times to perform the left-shift.
    @type count: int
    """
    j = 1
    for i in xrange( count ):
        yield j
        j <<= 1

@contextmanager
def wall_clock(output):
    """
    A simple timer for code sections.

    @param output: The resulting time is put into index 0 of L{output}.
    @type output: index-writeable

    Example:

        t = [0]
        with wall_clock(t):
            sleep(1)
        print "the sleep operation took %d seconds" % t[0]
    """
    start = time()
    try:
        yield
    finally:
        end = time()
        output[0] = end - start

def default_if_none(x, d):
    """
    Returns L{x} if it's not None, otherwise returns L{d}.
    """
    if x is None: return d
    else: return x

def seq(f, g):
    """
    Evaluate 0-ary functions L{f} then L{g}, returning L{g()}.
    """
    f()
    return g()
