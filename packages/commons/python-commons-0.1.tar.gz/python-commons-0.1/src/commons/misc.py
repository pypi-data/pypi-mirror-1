# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

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
