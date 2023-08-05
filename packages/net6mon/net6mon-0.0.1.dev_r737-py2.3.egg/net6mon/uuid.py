#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-


def unixgetaddr(program):
    """Get the hardware address on a Unix machine."""
    from os import popen
    for line in popen(program):
        words = line.lower().split()
        if 'hwaddr' in words:
            addr = words[words.index('hwaddr') + 1]
            return int(addr.replace(':', ''), 16)
        if 'ether' in words:
            addr = words[words.index('ether') + 1]
            return str(addr.replace(':', ''))

def wingetaddr(program):
    """Get the hardware address on a Windows machine."""
    from os import popen
    for line in popen(program + ' /all'):
        if line.strip().lower().startswith('physical address'):
            addr = line.split(':')[-1].strip()
            return str(addr.replace('-', ''))

def getaddr():
    """Get the hardware address as a 48-bit integer."""
    from os.path import join, isfile
    for dir in ['/sbin', '/usr/sbin', r'c:\windows',
                r'c:\windows\system', r'c:\windows\system32']:
        if isfile(join(dir, 'ifconfig')):
            return str(unixgetaddr(join(dir, 'ifconfig')))
        if isfile(join(dir, 'ipconfig.exe')):
            return str(wingetaddr(join(dir, 'ipconfig.exe')))


