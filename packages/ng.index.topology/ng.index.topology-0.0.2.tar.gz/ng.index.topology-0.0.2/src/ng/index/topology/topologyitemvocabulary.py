#######################################################################
"""Topology Item vocabulary for the Zope 3 based topology index package

$Id: topologyitemvocabulary.py 52787 2009-04-01 08:15:02Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52787 $"

from zope.interface import implements
from zope.app.container.interfaces import IContained
from ng.lib.simplevocabulary import SimpleVocabulary
from zope.schema.interfaces import  IContextSourceBinder, ITextLine
from zope.app.zapi import getUtilitiesFor
from interfaces import ITopologyContainer

def getcontainer(x) :
    try :
        return ITopologyContainer(x)
    except TypeError :
        return getcontainer(x.__parent__)

class TopologyItemVocabulary(object) :
    implements(IContextSourceBinder)

    def __call__(self, ob) :
        vocabulary = SimpleVocabulary.fromValues(
            sorted([ x for x,y in getcontainer(ob).items()]) #  if y.Id is None
        )
        return vocabulary

