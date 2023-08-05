# ieeemac.py
# Copyright (C) 2007, 2008 Justin Azoff JAzoff@uamail.albany.edu
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

"""Parses, finds, and converts MAC addresses between the following formats:
 bare:    001122334455
 windows: 00-11-22-33-44-55
 unix?:   00:11:22:33:44:55
 cisco:   0011.2233.4455

>>> from ieeemac import Mac, ismac
>>> ismac("00:11:22:33:44:55")
True
>>> ismac("00:11:22:33:44:5f")
True
>>> ismac("00:11:22:33:44:5g")
False
>>> m=Mac("00:11:22:33:44:5f")
>>> m.to_cisco
'0011.2233.445f'
>>> m.to_windows
'00-11-22-33-44-5f'
>>> m=Mac("00:1:2:3:4:5")
>>> m.to_windows
'00-01-02-03-04-05'
"""

import sys
import re

SEGMENT = "[0-9a-fA-F]{1,2}"
SIX = ((SEGMENT,)*6)

SEGMENT = "[0-9a-fA-F]{2}"
SIX_BARE = ((SEGMENT,)*6)

REGEXES = {
    'unix':      '(%s):(%s):(%s):(%s):(%s):(%s)' % SIX , 
    'windows':   '(%s)-(%s)-(%s)-(%s)-(%s)-(%s)' % SIX, 
    'cisco':     '(%s)(%s)\.(%s)(%s)\.(%s)(%s)'  % SIX_BARE, 
    'bare':      '(%s)(%s)(%s)(%s)(%s)(%s)'      % SIX_BARE,
}
ALL_REGEX = "(%s|%s|%s|%s)" % tuple(REGEXES.values())

FORMATS = {
    'unix':    '%s:%s:%s:%s:%s:%s',
    'windows': '%s-%s-%s-%s-%s-%s',
    'cisco':   '%s%s.%s%s.%s%s',
    'bare':    '%s%s%s%s%s%s',
}

for t,r in REGEXES.items():
    REGEXES[t] = re.compile(r + '$')
ALL_REGEX = re.compile(ALL_REGEX)

class Mac:
    def __init__(self, mac):
        if not mac:
            raise ValueError, "Invalid mac address: None"
        mac = mac.lower()
        for re_type, r in REGEXES.items():
            m = r.match(mac)
            if m:
                self.format = re_type
                self.groups = m.groups()
                #don't fix the groups here, most times I just want to init
                #the object to see if the mac is valid
                self.groups_need_fixing=True
                return

        raise ValueError, "Invalid mac address: %s" % mac
       

    def _formats(self):
        return FORMATS.keys()
    formats = property(_formats)

    def to_format(self, format):
        if self.groups_need_fixing:
            self.groups = tuple(["%02x" % int(x,16) for x in self.groups])
        return FORMATS[format] % self.groups

    def __getattr__(self, attr):
        if attr.startswith("to_"):
            format = attr[3:]
            return self.to_format(format)
        else:
            raise AttributeError

    def __str__(self):
        return self.to_format(self.format)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.to_windows == mac(other).to_windows
        else :
            return self.to_windows == other.to_windows

mac = Mac
def ismac(s):
    try:
        Mac(s)
        return True
    except ValueError:
        return False

def find_macs(text):
    """return any MAC addresses found in the text"""
    stuff = []
    for x in  ALL_REGEX.findall(text):
        m = Mac(x[0])
        stuff.append(m)
    return stuff


def main():
    if len(sys.argv)==1:
        print "Usage: %s mac_address" % sys.argv[0]
        sys.exit(1)

    m = Mac(sys.argv[1])

    print "Input mac address in %s format" % m.format

    for f in m.formats:
        print "%-10s %s" % (f, m.to_format(f))
