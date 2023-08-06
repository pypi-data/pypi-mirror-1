#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find orphan item in requires tree

$Id: subtrees_div.py 51094 2008-05-11 23:06:50Z cray $
"""
__author__  = "Andrey Orlov,  2008"
__license__ = "GPL"
__version__ = "$Revision: 51094 $"



class NodeSet(set) :
    __count_ = [0]
    __key_  = {}
    __trees_ = {}

    @property
    def __count__(self) :
        self.__count_[0]+=1
        return self.__count_[0]
                        
    def __init__(self,*kv,**kw) :
        super(NodeSet,self).__init__(*kv,**kw)
        self.__id__ = self.__count__
        self.__trees_[self.__id__] = self
        self.finish = set([])
        for key in self :
            self.key(key)

    def __getitem__(self,item) :
        return self.__key_[item]
        
    def key(self,key) :
        self.__key_[key] = self
        
    def add(self,key) :
        self.key(key)
        return super(NodeSet,self).add(key)                    

    def update(self,values) :
        for value in values :
            self.key(values)
        return super(NodeSet,self).update(values)

class TreeEnumerate(object) :
    def __init__(self,driver) :
        self.driver = driver
        self.common = set([])
        
    def tree_enumerate(self,roots) :
        for root in roots :
            if str(root) not in self.common :
                self.tree(NodeSet([root]))
                
    def tree(self,ns) :
        queue = [ self.driver[x] for x in ns]
    
        while queue :
            node = queue.pop()    

            for key,value in node.requires() :
                if key in self.common :
                    ns.finish.add(ns[key].__id__)
                elif key not in ns :
                    ns.add(key)
                    queue.append(value)
                
        self.common.update(ns)

    def tree_pass(self) :
        for key,values in NodeSet._NodeSet__trees_.items() :
            print key,values.finish
            if len(values.finish) :
                parent = values.__trees_[values.finish[0]]            
                parent.update(values)
        
    def __call__(self,roots) :
        self.tree_enumerate(roots)
        self.tree_pass()
        for item in NodeSet._NodeSet__trees_.values() :
            yield item
                              
    
def main() :

    import sys, os, libimalyzer
    from featurehideadapter import StorageAdapter

    driver = StorageAdapter(libimalyzer.driver())
    num = 0
    for items in TreeEnumerate(driver)(sys.argv[1:]) :
        num += 1
        print "Tree №",num
        for item in items :
            print "Tree node:", item
            sys.stdout.flush()
            
if __name__ == '__main__' :
    main()
         


                                
                                    
