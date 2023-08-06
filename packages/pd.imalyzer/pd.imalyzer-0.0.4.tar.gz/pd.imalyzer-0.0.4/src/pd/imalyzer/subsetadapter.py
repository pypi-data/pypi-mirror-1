### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to run dependence driver on subset nodes

$Id: subsetadapter.py 51090 2008-05-11 07:10:23Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 51090 $"

def _(s) : return s


from pd.lib.lazy import Lazy
from featurehideadapter import AdapterBase

class SubStorageAdapter(AdapterBase) :
    _ac= ['getItemByFeature','getItemByRequires']            
         
    def __init__(self,context,nodes) :
        super(SubStorageAdapter,self).__init__(context)
        self.nodes = dict( [ (str(value),SubFeatureAdapter(value,self)) for value in nodes] )         
                        
    def __getitem__(self,item) :
        return self.nodes[item]

    def has_key(self,item) :
        return self.nodes.has_key(item)

    def values(self) :
        return self.nodes.values()

    def items(self) :
        return self.nodes.items()

    def keys(self) :
        return self.nodes.keys()

class SubFeatureAdapter(AdapterBase) :
    _ac= ['__name__']

    def __init__(self,context,driver) :
        self.context = context
        self.driver = driver

    @Lazy
    def provides(self) :
        return [ (x,self.driver[x]) for x,y in self.context.provides() if self.driver.has_key(x)]

    @Lazy
    def requires(self) :
        return [ (x,self.driver[x]) for x,y in self.context.requires() if self.driver.has_key(x)]

