### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the features sources and customers.

$Id: interfaces.py 51055 2008-05-04 14:58:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51055 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
class IRequiresDriver(Interface) :
    
    requires = Set(
        title = u'Title',
        description = u'Title',
        default = u'',
        valuetype=TextLine,
        required = False)
                            
class IProvidesDriver(Interface) :

   provides = Set(
        title = u'Title',
        description = u'Title',
        default = u'',
        valuetype=TextLine,
        required = False)

class IFeatureStorageDriver(Interface) :

    title = TextLine(title=u"DriverName", readonly=True, require=True)

    def items(name,value): 
        """ Return all items in storage """
        
    def getItemByFeature(feature) :
        """ return all item which provide feature """
        
    def getItemByRequires (feature) :
        """ Return item which required feature """
                  

