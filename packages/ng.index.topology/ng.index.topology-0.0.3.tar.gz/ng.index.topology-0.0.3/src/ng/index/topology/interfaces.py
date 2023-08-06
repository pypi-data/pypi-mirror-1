### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.index.topology package

$Id: interfaces.py 53601 2009-08-15 21:50:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53601 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Set, Int, Choice
from zope.app.container.interfaces import IContained, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.catalog.interfaces import IAttributeIndex
from ng.lib.indexvocabulary import IndexVocabulary


class ITopologyContainerAllow(Interface) :
    pass

class ITopologyContainer(IOrderedContainer) :
    """ Interface for container with topologies """
    
    def __setitem__(name, object) :
        """ Add IArticle Content """

    __setitem__.precondition = ItemTypePrecondition(ITopologyContainerAllow)

from topologyitemvocabulary import TopologyItemVocabulary


class ITopologyContained(IContained) :
    """ Topology Contained """
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ITopologyContainer))

class ITopologyIndex(IAttributeIndex) :
    layer = Int(
                title = u"Outer layer",
                description = u"Items is near if layer less then this value",
                required=True,
                default = 3
                )

    beyond = Int(
                title = u"Inner layer",
                description = u"Items is near if layer more then this value",
                required=True,
                default = 0
                )

class INeighbour(Interface) : 
    neighbour = Set(
            title = u'Neighbour',
            description = u'Neighbour',
            value_type = Choice(
                    source = IndexVocabulary('neighbour')
                    ),
            default = set([]),
            required = False,
        )
                            

class ITopologyItem(Interface) : 
    Id = Int(
             title = u'Id',
             description = u'Id',
             readonly = True,
             required = False,
             default = None
         )

    neighbour = Set(
            title = u'Neighbour',
            description = u'Neighbour',
            value_type = Choice(source = TopologyItemVocabulary()),
            default = set([]),
            required = False,
        )
