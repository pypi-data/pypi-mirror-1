#!/usr/bin/python

import sys
import os
import getopt
import xattr

##
# Handle command line
##

# Defaults
attr_name  = None
attr_value = None

def usage(e=None):
    if e:
        print e
        print ""

    print "usage: %s file [attr_name [attr_value]]" % (sys.argv[0],)
    print "  With no optional arguments, lists the xattrs on file"
    print "  With attr_name only, lists the contents of attr_name on file"
    print "  With attr_value, set the contents of attr_name on file"

    if e: sys.exit(1)
    else: sys.exit(0)

# Read options
try:
    (optargs, args) = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.GetoptError, e:
    usage(e)

for optarg in optargs:
    if opt == "-h" or opt == "--help": usage()

if len(args):
    filename = args.pop(0)
else:
    usage("No file argument")

if len(args): attr_name  = args.pop(0)
if len(args): attr_value = args.pop(0)

##
# Do The Right Thing
##

attrs = xattr.xattr(filename)

if attr_name:
    if attr_value:
        attrs[attr_name] = attr_value
    else:
        if attr_name in attrs:
            print attrs[attr_name]
        else:
            print "No such attribute."
            sys.exit(1)
else:
    for name in attrs:
        print name
