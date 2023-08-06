### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannerrandnamespace.py 51701 2008-09-13 22:47:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51701 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.app.catalog.interfaces import ICatalog
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer
from ng.app.smartbanner.smartbanneralgorithm.interfaces import ISmartBannerAlgorithm

from zope.app.zapi import getUtility,getAdapter
import random

class SmartBannerRandNamespace(object) :
    implements(ITraversable)

    def __init__(self,context,request) :
        self.context = context
        self.request = request

    def traverse(self,name,ignored) :
        container = getUtility(ISmartBannerContainer,name=name,context=self.context)
        return getAdapter(container, ISmartBannerAlgorithm, name=container.algorithm).choice()
        
