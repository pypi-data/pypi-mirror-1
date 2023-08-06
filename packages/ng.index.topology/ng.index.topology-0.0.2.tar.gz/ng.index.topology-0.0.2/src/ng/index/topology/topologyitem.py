### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: topologyitem.py 52787 2009-04-01 08:15:02Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 52787 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ITopologyItem,ITopologyContained,ITopologyContainerAllow
from persistent import Persistent

from zope.app.container.contained import Contained
                
class TopologyItem(Contained, Persistent) :

    implements(ITopologyItem,ITopologyContained,ITopologyContainerAllow)

    Id = None
    
    neighbour = set([])

    def __init__(self, Id=None, value=None, *args, **kw):
        super(TopologyItem,self).__init__(self, *args, **kw)
        if value is None :
            self.neighbour = set([])
        else :
            self.neighbour = set(value)            
        self.Id = Id
        
        