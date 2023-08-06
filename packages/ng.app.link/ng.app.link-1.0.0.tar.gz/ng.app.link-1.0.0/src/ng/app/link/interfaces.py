### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based link package

$Id: interfaces.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Ischenko Valera"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, List, Object
from zope.app.container.interfaces import IContained, IContainer

class ILink(Interface):
    """ A link interface """
    
    id = Int (
           title=u"Unique id",
           description=u"Unique id",
           default=0,
           required=True,
           readonly=True)
                                                


