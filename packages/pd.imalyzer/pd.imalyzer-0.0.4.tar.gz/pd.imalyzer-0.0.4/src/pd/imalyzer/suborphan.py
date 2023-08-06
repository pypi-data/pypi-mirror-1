#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find orphan item in requires tree

$Id: suborphan.py 51069 2008-05-09 20:50:57Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51069 $"


def subtree(driver, name) :
    root = driver[name]
    nodes = set()
    for req in root.requires() :
        nodes = nodes | set([y for x,y in driver.getItemByFeature(req)])

    node = "nobody"
    l = []
    for node in nodes :
        for feature in node.provides() :
            for name, ob in driver.getItemByRequires(feature) :
                if name != str(root) :
                    break
            else :
                continue
            break
        else :
            yield node
                                        
def main() :
    import sys, os, libimalyzer
    driver = libimalyzer.driver()
    print "Check",sys.argv[1],"node on orphaned nodes after delete"
    for item in subtree(driver,sys.argv[1]) :
        print "Find orhpaned node:",item

if __name__ == '__main__' :
    main()
            