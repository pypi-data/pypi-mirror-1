### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Event handler for ITopologyItem object for the Zope 3 based package

$Id: topologyhandler.py 52823 2009-04-03 13:53:33Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52823 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ITopologyItem,ITopologyContained,ITopologyContainerAllow
from persistent import Persistent
from zope.security.proxy import removeSecurityProxy


from zope.app.container.interfaces import IContained
                
def handleAdded(ob,event) :
    container = IContained(ob).__parent__
    name = IContained(ob).__name__
    for item in ob.neighbour :
        container[item].neighbour = set(container[item].neighbour) | set([name])

def handleModified(ob,event) :
    container = IContained(ob).__parent__
    name = IContained(ob).__name__
    
    for value in container.values() :
       value = removeSecurityProxy(value)
       try :
           value.neighbour.remove(name)
       except KeyError:
           pass
       else :
           value._p_changed = 1

    for item in ob.neighbour :
        value = removeSecurityProxy(container[item])
        value.neighbour = set(value.neighbour) | set([name])
        value._p_changed = 1

def handleRemoved(ob,event) :
    container = IContained(ob).__parent__
    name = IContained(ob).__name__
    for item in ob.neighbour  :
        container[item].neighbour.remove(name)
        container[item]._p_changed = 1
        