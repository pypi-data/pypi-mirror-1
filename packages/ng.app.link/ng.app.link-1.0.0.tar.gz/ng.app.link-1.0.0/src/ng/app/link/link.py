### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The link class.

$Id: link.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"

from zope.interface import implements
from persistent import Persistent
from interfaces import ILink

from zope.app.intid.interfaces import IIntIds
from zope.component import getSiteManager
from zope.app.container.contained import Contained
from zope.app.zapi import getSiteManager
from zope.app.container.interfaces import IContained

class Link(Persistent, Contained):
    __doc__ = ILink.__doc__

    implements(ILink, IContained)
    
    def __init__(self, id):
        self.id = id
        
    