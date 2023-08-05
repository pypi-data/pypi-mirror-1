### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBanner class for the Zope 3 based smartbanner package

$Id: smartbanner.py 49270 2008-01-08 12:53:09Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49270 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.app.container.contained import Contained
from interfaces import ISmartBanner


class SmartBanner(Image, Contained) :

    implements(ISmartBanner)

    url = u""
    
    alt = u""
    
    border = False
    
    code = u'<a href="%(url)s" alt="%(alt)s"><img src="%(prefix)s%(name)s" border="%(border)s" alt="%(alt)s"></a>'

    begin_time = 0
    
    end_time = 86400
