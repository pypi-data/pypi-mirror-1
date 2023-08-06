# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Networking tools.
"""

import os, sys
from time import *
from contextlib import contextmanager

class NoMacAddrError( Exception ): pass

def get_mac_addr():
    """
    Simply parses the output of C{ifconfig} or C{ipconfig} to estimate
    this machine's IP address. This is not at all reliable, but tends
    to work "well enough" for my own purposes.

    From U{http://mail.python.org/pipermail/python-list/2005-December/357300.html}.

    @copyright: Frank Millman

    Note that U{http://libdnet.sf.net/} provides this functionality and much
    more.
    """
    mac = None
    if sys.platform == 'win32':
        for line in os.popen("ipconfig /all"):
            if line.lstrip().startswith('Physical Address'):
                mac = line.split(':')[1].strip().replace('-',':')
                break
    else:
        for line in os.popen("/sbin/ifconfig"):
            if line.find('Ether') > -1:
                mac = line.split()[4]
                break
    if mac is None:
        raise NoMacAddrError
    return mac

def retry_exp_backoff(initial_backoff, multiplier, func):
    """
    Repeatedly invoke L{func} until it succeeds (returns non-None), with
    exponentially growing backoff delay between each try.

    @param initial_backoff: The initial backoff.
    @type initial_backoff: float

    @param multiplier: The amount by which the backoff is multiplied on each
    failure.
    @type multiplier: float

    @param func: The zero-argument function to be invoked that returns True on
    success and False on failure.
    @type func: function

    @return: The result of the function
    """
    backoff = initial_backoff
    while True:
        res = func()
        if res is not None: return res
        print 'backing off for', backoff
        sleep(backoff)
        backoff = multiplier * backoff

@contextmanager
def logout(x):
    """
    A context manager for finally calling the C{logout()} method of an object.
    """
    try: yield x
    finally: x.logout()
