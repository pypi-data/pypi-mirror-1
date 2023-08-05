### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBanner class for the Zope 3 based smartbanner package

$Id: smartbanner.py 49685 2008-01-23 14:31:46Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49685 $"

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
