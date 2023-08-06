### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SmartBanner class for the Zope 3 based ng.app.smartbanner.smartbanner package

$Id: smartbanner.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.app.container.contained import Contained
from interfaces import ISmartBanner
from time import localtime
import datetime

class SmartBanner(Image, Contained) :

    implements(ISmartBanner)

    url = u""
    
    alt = u""
    
    border = False
    
    code = u'<a href="%(url)s" alt="%(alt)s"><img src="%(prefix)s%(name)s" border="%(border)s" alt="%(alt)s"></a>'

    begin_time = 0
    
    end_time = 86400

    begin_date = None
    
    end_date = None
    
    rate = 1

    disable = False

    def filter(self) :
        lt = localtime()
        lt_float = lt[3] * 60 * 60 + lt[4] * 60 + lt[5]
        
        return (
            not self.disable
            and ( 
                    self.begin_time < lt_float < self.end_time 
                or  (
                        self.begin_time > self.end_time 
                    and (
                            self.end_time < lt_float < 24 * 60 * 60 
                        or  0 < lt_float < self.begin_time
                        )
                    )
                )
            and (
                    self.begin_date is None
                or self.begin_date < datetime.date.today()
                )
            and (
                    self.end_date is None
                or self.end_date > datetime.date.today() 
                )
                                               
        )

