#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

NAME: meatoo.py 

DESC: Client for accessing meatoo database using XML-RPC

VERSION: 0.0.8

AUTHOR: Rob Cakebread <pythonhead a t gentoo dot 0rg>

LICENSE: GPL-2 (GNU Public License v.2)

"""

import xmlrpclib
import optparse
import sys

__docformat__ = 'restructuredtext'

[CAT, PN, DESC, PV, MAINTAINER, FM_DESC, FM_VERSION, FM_DATE,
 FM_URL, CHANGELOG ] = [i for i in range(10)]

SERVER_URL = "http://meatoo.gentooexperimental.org/xmlrpc/"


def print_results(results, options):
    """Print each line of results"""
    if results == [] or results[0][0] == "":
        return
    for pkg in results:
        print_line(pkg, options)


def print_line(pkg, options):
    """Print a single line in a nice format"""

    left = "%s/%s-%s [%s]" % (pkg[CAT], pkg[PN], pkg[PV], pkg[FM_VERSION])
    if options.today:
        print left.ljust(60) + pkg[MAINTAINER].lstrip()
    elif options.package or options.partial_package:
        print left + "  " + pkg[FM_DATE] + "  " + pkg[MAINTAINER]
    else:
        print left.ljust(60) + pkg[FM_DATE]


def send_request(options):
    """Send XML-RPC command"""

    server = xmlrpclib.ServerProxy(SERVER_URL)
    if options.package:
        results = server.getPackage(options.package)
    elif options.last:
        results = server.getLast()
    elif options.partial_package:
        results = server.getPartialPackage(options.partial_package)
    elif options.catpackage:
        results = server.getCatPackage(options.catpackage)
    elif options.maint:
        results = server.getMaintainer(options.maint)
    elif options.date:
        results = server.getDate(options.date)
    elif options.today:
        results = server.getLatest()
    print_results(results, options)


def main():
    """Parse command-line arguments and do it."""

    opt_parser = optparse.OptionParser()
    opt_parser.add_option("-l", action="store_true", dest="last",
                          default=False, help=
                          "List last 20 packages needing version bumps."
                          )
    opt_parser.add_option("-m", action="store", dest="maint", default=
                          False, help=
                          "List packages by herd or maintainer email address."
                          )
    opt_parser.add_option("-p", action="store", dest="package", default=
                          False, help="List by exact package name.")
    opt_parser.add_option("-P", action="store", dest="partial_package",
                          default=False, help=
                          "List by partial package name.")
    opt_parser.add_option("-c", action="store", dest="catpackage",
                          default=False, help=
                          "List by exact category/package name.")
    opt_parser.add_option("-d", action="store", dest="date", default=
                          False, help="List by Freshmeat release date.")
    opt_parser.add_option("-t", action="store_true", dest="today",
                          default=False, help=
                          "List today's Freshmeat releases.")
    (options, remaining_args) = opt_parser.parse_args()

    if len(sys.argv) < 2 or remaining_args:
        opt_parser.print_help()
        sys.exit(2)
    send_request(options)


if __name__ == "__main__":
    main()
