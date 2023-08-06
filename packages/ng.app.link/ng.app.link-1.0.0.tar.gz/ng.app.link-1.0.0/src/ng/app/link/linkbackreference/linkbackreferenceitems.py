### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The linkbackreferenceitem class.

$Id: linkbackreferenceitems.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"

from zope.interface import implements
from interfaces import ILinkBackReferenceItems,ILinkBackReferenceItemsContained
from persistent.list import PersistentList
from zope.app.container.contained import Contained

class LinkBackReferenceItems(Contained,PersistentList):
    __doc__ = ILinkBackReferenceItems.__doc__

    implements(ILinkBackReferenceItems,ILinkBackReferenceItemsContained)
    
    def append(self,item) :
        if item not in self :
            super(LinkBackReferenceItems,self).append(item)
        
        
        
        
            