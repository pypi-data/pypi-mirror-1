### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBannerDumb class for the Zope 3 based ng.app.smartbanner package

$Id: smartbannerdumb.py 51936 2008-10-23 08:14:17Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51936 $"

from zope.interface import Interface
from zope.interface import implements
from interfaces import ISmartBannerDumb

class SmartBannerDumb(object) :

    implements(ISmartBannerDumb)
