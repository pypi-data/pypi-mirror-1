#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find tree which required only
removed item

$Id: subtree.py 51075 2008-05-10 00:52:57Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51075 $"


def subtree(driver, name) :
    queue = [driver[name]]
    d = {}
    while queue :
        item = queue.pop() 
        for key,value in item.requires() :
            if not d.has_key(key) :
                queue.append(value)
                d[key] = value
                
    for value in d.values() :
        for key,require in value.provides() :
            if not d.has_key(key) :
                break
        else :                
            yield value
                                        
def main() :
    import sys, os, libimalyzer
    from featurehideadapter import StorageAdapter

    driver = StorageAdapter(libimalyzer.driver())
    print "Check",sys.argv[1],"node on orphaned nodes after delete"
    for item in subtree(driver,sys.argv[1]) :
        print "Find orhpaned node:",item

if __name__ == '__main__' :
    main()
            