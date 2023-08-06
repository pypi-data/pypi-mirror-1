### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The linkbackreference class.

$Id: linkbackreference.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"

from zope.interface import implements
from interfaces import ILinkBackReference,ILinkBackReferenceContained,ILinkBackReferenceContainer
from zope.app.container.btree import BTreeContainer
from linkbackreferenceitems import LinkBackReferenceItems
from zope.app import zapi
from zope.app.intid.interfaces import IIntIds


class LinkBackReference(BTreeContainer):
    __doc__ = ILinkBackReference.__doc__

    implements(ILinkBackReference,ILinkBackReferenceContained,ILinkBackReferenceContainer)
    

    def handleAdd(self,ref) :
        name = "c%016u" % ref.id
       
        try :
            items = self[name]   
        except KeyError :
            items = self[name] = LinkBackReferenceItems()
            
        items.append("c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ref))            
        
    def handleDel(self,ref) :
        name = "c%016u" % ref.id
       
        try :
            items = self[name]   
        except KeyError :
            return
            
        items.remove("c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ref))        
        
    def handleDelOb(self,ob) :
        self.handleCleanOb(ob)
        name = "c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ob)
        try :
            del(self[name])
        except KeyError, msg :
            print "Can't clean object from newsbackreference index becouse of",msg            

    def cleanAll(self) :
        for item in self.keys() :
            self.handleCleanItem(item)

    def handleCleanOb(self,ob) :
        self.handleCleanItem("c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ob))
        
    def handleCleanItem(self,name) :
        try :
            items = self[name]   
        except KeyError :
            return

        for item in list(items) :
            try :
                ref = zapi.getUtility(IIntIds, self.newsRefId).getObject(int(item[1:]))
                del(ref.__parent__[ref.__name__])
                
            except KeyError,msg :
                print "Can't remove reference becouse of",msg

    