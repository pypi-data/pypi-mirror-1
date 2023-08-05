### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBannerView class for the Zope 3 based smartbannerview package

$Id: smartbannerview.py 49270 2008-01-08 12:53:09Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49270 $"

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
        lt = time.localtime()
        lt_float = lt[3] * 60 * 60 + lt[4] * 60 + lt[5]
        banners = [x for x in zapi.getUtility(ISmartBannerContainer).values() if x.begin_time < lt_float < x.end_time]
        return banners
