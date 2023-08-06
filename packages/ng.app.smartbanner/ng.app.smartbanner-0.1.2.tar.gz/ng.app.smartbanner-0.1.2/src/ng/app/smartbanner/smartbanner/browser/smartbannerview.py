### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBannerView class for the Zope 3 based
ng.app.smartbanner.smartbanner package

$Id: smartbannerview.py 51936 2008-10-23 08:14:17Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51936 $"


from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app import zapi
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer, ISmartBannerContainerData

from zope.schema import getFieldNames
from ng.app.smartbanner.smartbanner.interfaces import ISmartBanner, ISmartBannerData
from zope.traversing.browser import absoluteURL

                
class SmartBannerView(object) :
    """ SmartbannerView
    """    

    @property    
    def code(self):
        """ fill code property with values
        """
        sb = ISmartBannerData(self.context)

        d = dict([ (x, getattr(sb, x)) for x in  getFieldNames(ISmartBannerData)])

        if d['border'] == False :
            d['border'] = 0
        else :
            d['border'] = 1


        if ISmartBannerContainerData(self.context.__parent__).use_fake_place :
            d['prefix'] = ISmartBannerContainerData(self.context.__parent__).fake_place_root
            d['name'] = self.context.__name__
        else :
            d['prefix'] = absoluteURL(self.context.__parent__, self.request)
            d['name'] = u'/'+self.context.__name__

        return self.context.code % d
