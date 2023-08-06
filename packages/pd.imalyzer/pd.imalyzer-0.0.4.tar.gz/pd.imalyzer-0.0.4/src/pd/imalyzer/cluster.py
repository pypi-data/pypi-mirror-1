#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find orphan item in requires tree

$Id: cluster.py 51092 2008-05-11 10:31:07Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51092 $"

def cluster_enumerate(driver) :
    excludes = set([])
    while True :
        for node in driver.values() :
            if str(node) not in excludes :
                break
        else :
            raise StopIteration
        yield cluster(driver,excludes,node)                

def cluster(driver,excludes,root) :
    cl = set([str(root)])
    queue=[root]
    while queue :
        node = queue.pop()
        yield node
        
        for key,value in [(x,y) for x,y in node.requires() ] + [(x,y) for x,y in node.provides() ] :
            if key not in cl and key not in excludes :
                cl.add(key)
                queue.insert(0,value)

    excludes.update(cl)
    
def main() :
    import sys, os, libimalyzer
    from featurehideadapter import StorageAdapter
    from subsetadapter import SubStorageAdapter
    driver = StorageAdapter(libimalyzer.driver())    
    driver = SubStorageAdapter(driver, [ driver[x] for x in sys.argv[1:] ])
    num = 0
    for items in cluster_enumerate(driver) :
        num += 1
        print "cluster №",num
        for item in items :
            print "Cluster node:", item
            sys.stdout.flush()
            
if __name__ == '__main__' :
    main()
         


                                
                                    
