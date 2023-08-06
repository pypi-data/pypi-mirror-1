#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to do segmentation of dependence graph.

$Id: imalyzer.py 51095 2008-05-12 07:31:09Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51095 $"


from kernel import KernelValue, orphan_enumerate
from subtrees import tree_enumerate
import sys, os, libimalyzer
from featurehideadapter import StorageAdapter
from cluster import cluster_enumerate
from subsetadapter import SubStorageAdapter


def main() :
    driver = StorageAdapter(libimalyzer.driver())
    num = 0
    try :
        # Search Kernel
        layeritems = []
        for layer in orphan_enumerate(driver) :
            num += 1
            for item in layer :
                layeritems.insert(0,item)
    except KernelValue,(kernel,) :
        # Get kernel by exception
        print "Kernel len:",len(kernel)
         
        num = 0
        for items in cluster_enumerate(SubStorageAdapter(driver,[ driver[x] for x in kernel ])) :
            num += 1
            print "Kernlel cluster #",num
            for item in items :
                print num, ":", item
                sys.stdout.flush()
                        
    # Shell clusterization on tree
    num = 0
    for items in tree_enumerate(driver,layeritems) :
        num += 1
        print "Shell cluster #",num
        for item in items :
            print num,":", item
            sys.stdout.flush()
                
       
if __name__ == '__main__' :
    main()
