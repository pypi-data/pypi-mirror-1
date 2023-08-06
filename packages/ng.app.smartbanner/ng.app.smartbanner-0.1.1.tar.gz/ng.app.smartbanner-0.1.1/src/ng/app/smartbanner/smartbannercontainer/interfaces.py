### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51701 2008-09-13 22:47:48Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51701 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Choice
from zope.app.container.interfaces import IContained, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

class ISmartBannerContent ( Interface ) :
    pass

class ISmartBannerContainerData(Interface) :
    
    use_fake_place = Bool(
                     title=u"Use fake place",
                     description=u"True if this node is expanded.",
                   )

    fake_place_root = TextLine(
        title = u'Fake place root',
        description = u'fake_place_root',
        default = u'',
        required = False)

    algorithm = Choice(
        title = u'Algorithm',
        description = u'Algorithm that be used to choice current banner',
        vocabulary = 'SmartBannerAlgorithmVocabulary',
        default = 'Random',
    )

class ISmartBannerContainer ( IOrderedContainer ) :
    """ """
    def __setitem__(name, object) :
        """ Add a ISmartBannerContent object. """
    __setitem__.precondition = ItemTypePrecondition(ISmartBannerContent)
    
class ISmartBannerContainerOrdered ( ISmartBannerContainer ) :
    """ """