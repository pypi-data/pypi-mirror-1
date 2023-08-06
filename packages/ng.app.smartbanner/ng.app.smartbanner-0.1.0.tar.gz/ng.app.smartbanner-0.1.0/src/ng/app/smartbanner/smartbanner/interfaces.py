### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.smartbanner.smartbanner package

$Id: interfaces.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Date, Int, URI
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.file.interfaces import IImage

from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer

from ng.schema.floatdaytime.floatdaytime import FloatDayTime


class ISmartBannerData(Interface) :
    """ ISmartBannerData interface
    """
    
    url = URI(
        title = u"Target URL",
        description = u"Target URL assiciated with banner",
        required = False
        )

    alt = TextLine(
        title = u"Alternative text",
        description = u"Alternative text",
        default = u"",
        required = False
        )

    border = Bool(
        title = u"Show border",
        description = u"Show border",
        default = False,
        required = False
        )

    code = Text(
        title = u"Code of banner",
        description = u"Code of banner",
        default = u"""<a href="%(url)s" title="%(alt)s"><img src="%(prefix)s%(name)s" border="%(border)s" alt="%(alt)s"/></a>""",
        required = False
        )

    begin_time = FloatDayTime(
        title = u"Start time",
        description = u"Start time",
        required = False
        )

    end_time = FloatDayTime(
        title = u"End time",
        description = u"End time",
        required = False
        )

    rate = Int(
        title=u"Banner rate",
        description=u"Banner rate",
        required = True,
        default = 1,
        min = 1,
        max = 100
        )

    begin_date = Date(
        title=u"Banner show begin date",
        description=u"The date when banner show begun",
        required= False,
        default=None
        )
        
    end_date = Date(
        title=u"Banner show finish date",
        description=u"The date when banner show finish",
        required= False,
        default=None
        )
        
    disable = Bool(
        title = u"Disable",
        description = u"Disable banner show",
        required=False,
        default=False
        )

class ISmartBannerMethod(Interface) :
    """ Methods of smartbanner """
    
    def filter() :
        """Filter to allow show banner"""        
    

class ISmartBanner(ISmartBannerMethod, ISmartBannerData, IImage) :
    """ ISmartBanner interface
    """
    

class ISmartBannerContained(IContained) :
    """ ISmartBanerContained interface
    """
    __parent__ = Field(constraint = ContainerTypesConstraint(ISmartBannerContainer))
