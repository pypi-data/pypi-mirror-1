#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find orphan item in requires tree

$Id: subtrees.py 51087 2008-05-11 04:47:44Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51087 $"


def tree_enumerate(driver,roots) :
    trees = {}
    common = set([])
    for root in roots :
        if str(root) not in common :
            st = set([])
            trees[str(root)] = st 
        
            yield tree(driver[root],common,st,trees)
 

def tree(root,common,st,trees) :
    queue = [root]
    st.add(root)
    
    while queue :
        node = queue.pop()    

        for key,value in node.requires() :
            if key not in common :
                if key not in st :
                    st.add(key)
                    queue.append(value)
                    yield value
        
    common.update(st)
    for key in st :
        trees[key] = st
    
def main() :

    import sys, os, libimalyzer
    from featurehideadapter import StorageAdapter

    driver = StorageAdapter(libimalyzer.driver())
    num = 0
    for items in tree_enumerate(driver,sys.argv[1:]) :
        num += 1
        print "Tree №",num
        for item in items :
            print "Tree node:", item
            sys.stdout.flush()
            
if __name__ == '__main__' :
    main()
         


                                
                                    
