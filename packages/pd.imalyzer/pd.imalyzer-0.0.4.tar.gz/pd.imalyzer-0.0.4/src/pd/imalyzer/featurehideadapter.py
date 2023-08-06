### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to hide features from dependence driver and 
represent its only as node to require or provide.

$Id: featurehideadapter.py 51077 2008-05-10 01:16:36Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 51077 $"

def _(s) : return s


from pd.lib.lazy import Lazy


class AdapterBase(object) :
    _ac= []

    def __init__(self,context) :
        self.context = context
        
    def __getattr__(self,name) :
        if name in self._ac :
            return getattr(self.context,name)

    def __repr__(self) :
        return self.context.__repr__()

    def __str__(self) :
        return self.context.__str__()
        

class StorageAdapter(AdapterBase) :
    _ac= ['items','__getitem__', 'keys', 'getItemByFeature','getItemByRequires']            
                        
    @Lazy    
    def __getitem__(self,item) :
        return FeatureAdapter(self.context[item])

    @Lazy
    def values(self) :
        return [ self[x] for x in self.context.keys() ]

    @Lazy
    def items(self) :
        return [ (x,self[x]) for x in self.context.keys() ]


class FeatureAdapter(AdapterBase) :
    _ac= ['__name__']


    @Lazy
    def provides(self) :
        dp = {}
        for feature in self.context.provides() :
            for name,value in self.context.driver.getItemByRequires(feature) :
                dp[name] = value
                
        return [ (x,FeatureAdapter(y)) for x,y in dp.items()]

    @Lazy
    def requires(self) :
        dp = {}
        for require in self.context.requires() :
            for name,value in self.context.driver.getItemByFeature(require) :
                dp[name] = value
                
        return [ (x,FeatureAdapter(y)) for x,y in dp.items()]
        
    @Lazy
    def required(self) :
        dp = {}
        for feature in self.context.provides() :        
            for name,value in self.context.driver.getItemByFeature(feature) :
                dp[name] = value
                
        return [ (x,FeatureAdapter(y)) for x,y in dp.items()]
        
        
                            
            
    
