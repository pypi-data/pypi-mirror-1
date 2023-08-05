# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Networking tools.
"""

import os, sys

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

