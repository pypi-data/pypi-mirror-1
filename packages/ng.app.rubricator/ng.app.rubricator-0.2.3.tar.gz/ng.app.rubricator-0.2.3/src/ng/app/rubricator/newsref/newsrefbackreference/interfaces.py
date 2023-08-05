### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based newsrefbackreference package

$Id: interfaces.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov 2006 12 03"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ItemTypePrecondition

class INewsRefBackReference(Interface):
    """ A newsrefbackreference interface """

    newsRefId = Choice(title = u'Name of Int Ids',
                        description = u'Name of IntIds utility,'
                                        ' used for registering'
                                        ' newsref in rubrics',
                        default = None,
                        required = True,
                        vocabulary = 'IntIdsNames'
                        )

class INewsRefBackReferenceContained(IContained):
    """Interface that specifies the type of objects that can contain NewsRefBackReference"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager,ISiteManagementFolder))

class INewsRefBackReferenceItems(Interface):
    """ A newsrefbackreferenceitems interface """
    pass

class INewsRefBackReferenceItemsContained(IContained):
    """Interface that specifies the type of objects that can contain NewsRefBackReferenceItems"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(INewsRefBackReference))

class INewsRefBackReferenceContainer(IContainer) :
    def __setitem__(key, value):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(INewsRefBackReferenceItemsContained)
