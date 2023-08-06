### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Item of topology index container. Each item correspond to node of graph topology relation.

$Id: topologyitem.py 53601 2009-08-15 21:50:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53601 $"

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
        
        