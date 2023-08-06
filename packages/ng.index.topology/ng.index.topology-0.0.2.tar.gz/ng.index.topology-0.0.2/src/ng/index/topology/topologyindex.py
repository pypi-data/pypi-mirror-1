### -*- coding: utf-8 -*- #############################################
#######################################################################
"""TopologyIndex class for the Zope 3 based TopologyIndex package

$Id: topologyindex.py 52807 2009-04-02 21:49:59Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52807 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy

from topologybase import TopologyBase
from topologycontainer import TopologyContainer
from interfaces import ITopologyIndex
from zope.app.catalog.interfaces import ICatalogIndex
from zope.app.catalog.attribute import AttributeIndex

from zope.index.interfaces import IInjection, IStatistics, IIndexSearch
from topologyitem import TopologyItem
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
                
class TopologyIndexBase(TopologyBase,TopologyContainer) :
    implements(ITopologyIndex,ICatalogIndex, IInjection, IStatistics, IIndexSearch)

    interface = None
    
    field_name = ""
    
    field_callable = False
                        
    # IInjection
    
    def index_doc(self,docid,value) :
        print value
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
        return list(self._apply(query))
    def _apply(self,query) :
        nlayer = self.layer
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

        result = nextlayer.copy()
        for i in range(0,nlayer) :
            print i
            layer = nextlayer
            nextlayer = set([])                    
            while(layer) :
                key = layer.pop()
                item = self[key]
                #print "!!!!",key,item.neighbour,result
                s = set(item.neighbour) - result
                nextlayer.update(s)
                #print "--->",nextlayer
                result.update(s)
                print "result",key
                if not item.Id is None :
                    yield item.Id
        
    # IIndexSearch
    def documentCount(self):
        """Return the number of documents currently indexed."""
        return len(self)
           
    def wordCount():
        """Return the number of words currently indexed."""
        return len(self)

class TopologyIndex(AttributeIndex,TopologyIndexBase) :
    pass
