### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based linkbackreference package

$Id: interfaces.py 51546 2008-08-30 22:07:37Z cray $
"""
__author__  = "Andrey Orlov 2006 12 03"
__license__ = "GPL"
__version__ = "$Revision: 51546 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ItemTypePrecondition

class ILinkBackReference(Interface):
    """ A linkbackreference interface """

    newsRefId = Choice(title = u'Name of Int Ids',
                        description = u'Name of IntIds utility,'
                                        ' used for registering'
                                        ' link in rubrics',
                        default = None,
                        required = True,
                        vocabulary = 'IntIdsNames'
                        )

    def cleanAll(self) :
      """ Clean all links from site """
      pass

class ILinkBackReferenceContained(IContained):
    """Interface that specifies the type of objects that can contain LinkBackReference"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager,ISiteManagementFolder))

class ILinkBackReferenceItems(Interface):
    """ A linkbackreferenceitems interface """
    pass

class ILinkBackReferenceItemsContained(IContained):
    """Interface that specifies the type of objects that can contain LinkBackReferenceItems"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILinkBackReference))

class ILinkBackReferenceContainer(IContainer) :
    def __setitem__(key, value):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(ILinkBackReferenceItemsContained)
