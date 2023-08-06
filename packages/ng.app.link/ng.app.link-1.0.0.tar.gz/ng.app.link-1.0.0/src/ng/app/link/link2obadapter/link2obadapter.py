### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter used to select content from link.

$Id: link2obadapter.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"
__credits__ = """Andrey Orlov, for idea and common control"""

from ng.app.link.interfaces import ILink
from zope.app.intid.interfaces import IIntIds
from zope.app.zapi import getUtility
from zope.component import ComponentLookupError

def Link2ObAdapter(link):
    """Select content from link"""
    try :
        intids = getUtility(IIntIds,context=link)
    except ComponentLookupError,msg :
        print "IIntIds Lookup Error",msg
        raise
        
    return intids.getObject(ILink(link).id)
    