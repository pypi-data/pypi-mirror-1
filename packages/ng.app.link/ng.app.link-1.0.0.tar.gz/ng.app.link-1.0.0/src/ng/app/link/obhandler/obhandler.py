### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
news storage, to remove link objects 

$Id: obhandler.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"

from zope.component import ComponentLookupError
from zope.app import zapi
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
    
def handleDel(ob,event) :
    try :
        for (name,br) in zapi.getUtilitiesFor(ILinkBackReference, ob) :
            br.handleDelOb(ob)
    except ComponentLookupError,msg :
        print "Could't find INewsBackReference:",msg

