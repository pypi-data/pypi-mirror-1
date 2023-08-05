### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannernamespace.py 49270 2008-01-08 12:53:09Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49270 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.app.catalog.interfaces import ICatalog
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer

from zope.app.zapi import getUtility

class SmartBannerNamespace(object) :
    implements(ITraversable)

    def __init__(self,context,request) :
        self.context = context
        self.request = request

    def traverse(self,name,ignored) :
        sbc = getUtility(ISmartBannerContainer)
        return sbc[name]
        