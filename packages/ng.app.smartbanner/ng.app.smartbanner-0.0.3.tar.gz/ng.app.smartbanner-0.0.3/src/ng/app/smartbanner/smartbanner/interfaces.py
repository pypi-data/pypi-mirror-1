### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based smartbanner package

$Id: interfaces.py 49685 2008-01-23 14:31:46Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49685 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, URI
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
        default = u"""<a href="%(url)s" alt="%(alt)s"><img src="%(prefix)s%(name)s" border="%(border)s" alt="%(alt)s"></a>""",
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


class ISmartBanner(ISmartBannerData, IImage) :
    """ ISmartBanner interface
    """

class ISmartBannerContained(IContained) :
    """ ISmartBanerContained interface
    """
    __parent__ = Field(constraint = ContainerTypesConstraint(ISmartBannerContainer))
