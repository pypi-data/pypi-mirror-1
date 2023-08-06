#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to serve imalyzer package

$Id: libimalyzer.py 51064 2008-05-06 01:22:51Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51064 $"

import sys, os
def driverbyname(name) :
    module = ".".join(name.split(".")[0:-1])
    driver = getattr( __import__( module, globals(), locals(), module), name.split(".")[-1])()
    print "Load:",driver.name
    return driver
        
def driver() :
    try :
        name=sys.argv[1]
    except IndexError :
        print "Please, use: ",sys.argv[0],"<feature driver> [any optional arguments]"        
        sys.exit(0)
    else :        
        del sys.argv[1]
        return driverbyname(name)
