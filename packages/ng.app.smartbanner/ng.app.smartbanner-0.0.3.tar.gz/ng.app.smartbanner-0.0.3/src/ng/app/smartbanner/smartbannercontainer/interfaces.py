### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49685 2008-01-23 14:31:46Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49685 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

class ISmartBannerContent ( Interface ) :
    pass

class ISmartBannerContainerData(Interface) :
    
    use_fake_place = Bool(
                     title=u"use_fake_place",
                     description=u"True if this node is expanded.",
                   )

    fake_place_root = TextLine(
        title = u'fake_place_root',
        description = u'fake_place_root',
        default = u'',
        required = False)

class ISmartBannerContainer ( IOrderedContainer ) :
    """ """
    def __setitem__(name, object) :
        """ Add a ISmartBannerContent object. """
    __setitem__.precondition = ItemTypePrecondition(ISmartBannerContent)
    
class ISmartBannerContainerOrdered ( ISmartBannerContainer ) :
    """ """    