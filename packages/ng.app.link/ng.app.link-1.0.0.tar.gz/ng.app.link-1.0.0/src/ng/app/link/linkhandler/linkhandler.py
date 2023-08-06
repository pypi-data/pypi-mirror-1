### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
linkbackreference storage, to index link objects 

$Id: linkhandler.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"

from zope.component import ComponentLookupError
from zope.app import zapi
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
from ng.app.link.interfaces import ILink

def handleAdd(ob,event) :
    try :
        for (name,br) in zapi.getUtilitiesFor(ILinkBackReference, ob) :
            br.handleAdd(ob)
    except ComponentLookupError,msg :
        print "Could't find INewsBackReference:",msg
    
def handleDel(ob,event) :
    try :
        for (name,br) in zapi.getUtilitiesFor(ILinkBackReference, ob) :
            br.handleDel(ob)
    except ComponentLookupError,msg :
        print "Could't find INewsBackReference:",msg
        