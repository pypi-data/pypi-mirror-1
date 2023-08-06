### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannernamespace.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.app.catalog.interfaces import ICatalog
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer

from zope.app.zapi import getUtility, getUtilitiesFor

class SmartBannerNamespace(object) :
    implements(ITraversable)

    def __init__(self,context,request) :
        self.context = context
        self.request = request

    def traverse(self,key,ignored) :
        try :
            key,name = key.rsplit(":",1)
        except ValueError :
            for name, utility in getUtilitiesFor(ISmartBannerContainer) :
                try :
                    return utility[key]
                except KeyError :
                    pass
            else :
                raise KeyError, key                               
        else :
            return getUtility(ISmartBannerContainer,name=name)[key]        
            