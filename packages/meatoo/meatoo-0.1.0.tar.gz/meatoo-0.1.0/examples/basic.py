#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

NAME: basic.py 

DESC: Very simple example of XML-RPC API

VERSION: 0.0.1

AUTHOR: Rob Cakebread <pythonhead a t gentoo dot 0rg>

LICENSE: GPL-2 (GNU Public License v.2)

"""

import xmlrpclib

__docformat__ = 'restructuredtext'


SERVER_URL = "http://meatoo.gentooexperimental.org/xmlrpc"


def main():
    """Try a few queries"""
    server = xmlrpclib.ServerProxy(SERVER_URL)
    print server.getLast()
    print server.getLatest()
    print server.getMaintainer("python")

if __name__ == "__main__":
    main()
