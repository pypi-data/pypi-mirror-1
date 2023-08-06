### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Contaier class for the Zope 3 based TopologyIndex package

$Id: topologycontainer.py 52764 2009-03-31 14:19:49Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52764 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.container.ordered import OrderedContainer
from interfaces import ITopologyContainer
                
class TopologyContainer(OrderedContainer) :
    implements(ITopologyContainer)

                    
