#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find orphan item in requires tree

$Id: orphan.py 51078 2008-05-10 01:17:47Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51078 $"


class KernelValue(Exception) :
    pass

def orphan_enumerate(driver) :
    nodes = dict(driver.items())
    exclude = {}
    while nodes :
        yield orphan(driver,nodes,exclude)        

def orphan(driver,nodes,exclude) :
    num = 0
    ex = {}
    for key,node in nodes.items() :
        for k,v in node.provides() :
            if k not in exclude :
                break
        else :
            del nodes[key]
            ex[key] = node
            num += 1
            yield node

    exclude.update(ex)
            
    if num == 0 :
        raise KernelValue,(nodes,)    

def main() :
    import sys, os, libimalyzer
    from featurehideadapter import StorageAdapter
    driver = libimalyzer.driver()
    num = 0
    try :
        for layer in orphan_enumerate(StorageAdapter(driver)) :
            num += 1
            print "Layer №",num,":"
            for item in layer :
                print "Layer №",num,"orphaned node:", item
                sys.stdout.flush()
    except KernelValue,(kernel,) :
        print "Kernel:",len(kernel)
        for item in sorted(kernel.keys()) :
            print "kernel",item                
            sys.stdout.flush()
       
if __name__ == '__main__' :
    main()
         


                                
                                    
