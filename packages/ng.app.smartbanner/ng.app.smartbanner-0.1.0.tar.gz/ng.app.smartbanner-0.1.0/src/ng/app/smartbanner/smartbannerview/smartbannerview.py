### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBannerView class for the Zope 3 based
ng.app.smartbanner.smartbannerview package

$Id: smartbannerview.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"


from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app import zapi
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer
import time


class SmartBannerView(object) :
    """ SmartbannerView
    """    
    
    @property
    def banners(self):
        """ Get images from ISmartBannerContainer utility and set banners property
            from them
        """
        return (x for x in zapi.getUtility(ISmartBannerContainer).values() if x.filter())

  
