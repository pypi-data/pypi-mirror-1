### -*- coding: utf-8 -*- #############################################
#######################################################################
"""TopologyIndex class for the Zope 3 based TopologyIndex package

$Id: topologyindex.py 53601 2009-08-15 21:50:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53601 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy

from topologybase import TopologyBase
from topologycontainer import TopologyContainer
from interfaces import ITopologyIndex, ITopologyItem
from zope.app.catalog.interfaces import ICatalogIndex
from zope.app.catalog.attribute import AttributeIndex

from zope.index.interfaces import IInjection, IStatistics, IIndexSearch
from zc.catalog.interfaces import IIndexValues
from topologyitem import TopologyItem
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
from BTrees.IFBTree import IFBucket
                
class TopologyIndexBase(TopologyBase,TopologyContainer) :
    implements(ITopologyIndex,ICatalogIndex, IInjection, IStatistics, IIndexSearch, IIndexValues)

    interface = None
    
    layer = 3
    
    beyond = 0
    
    field_name = ""
    
    field_callable = False
                        
    # IInjection
    
    def index_doc(self,docid,value) :
        if unicode(docid) in self :
            del self[unicode(docid)]
        self[unicode(docid)] = TopologyItem(int(docid),set(self.keys()) & set(value))
        
    def unindex_doc(self,docid) :
        try :
            del self[unicode(docid)]
        except KeyError,msg :
            print "KeyError",msg
            pass            
    
    def clear(self) :  
        for name,value in list(self.items()) :
            if value.Id is not None :
                del self[name]

    # IIndexSearch
    
    def apply(self,query) :
        return IFBucket(list(self._apply(query)))

    def _apply(self,query) :
        nlayer = self.layer
        beyond = self.beyond
        if type(query) in [set,list,tuple] :
            nextlayer = set(query)
        elif type(query) in [dict] :
            if query.has_key('object') :
                nextlayer = set([unicode(getUtility(IIntIds,context=self).getId(query['object']))])
            else :
                nextlayer = set(query['query'])

            try :
                nlayer = query['layer']
            except KeyError :
                pass                

            try :
                beyond = query['beyond']
            except KeyError :
                pass                

        result = nextlayer.copy()
        for i in range(0,nlayer) :
            layer = nextlayer
            nextlayer = set([])                    
            while(layer) :
                key = layer.pop()
                try :
                    item = self[key]
                except KeyError,msg :
                    print "Search word does not exist:", msg
                else :                    
                    s = set(item.neighbour) - result
                    nextlayer.update(s)
                    result.update(s)
                    if not item.Id is None and i >= beyond :
                        yield (item.Id,-i)
        
    # IIndexSearch
    def documentCount(self):
        """Return the number of documents currently indexed."""
        return len(self)
           
    def wordCount(self):
        """Return the number of words currently indexed."""
        return len(self)

    # IIndexValues
    def maxValue(self,max=None) :
        return max(self.values())

    def containsValue(self,value) :
        return value in self and not ITopologyItem(self[value]).Id
        
    def values(self,min=None, max=None, excludemin=False, excludemax=False, doc_id=None) :
        for key in sorted(self.keys()) :
            ob = self[key]
            if ITopologyItem(ob).Id is None :
                yield key
        
    def ids(self) :
        return []
                
    def minValue(self,min=None) :
        return min(self.values())
    

class TopologyIndex(AttributeIndex,TopologyIndexBase) :
    pass
