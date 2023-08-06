### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannercontainer.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"

from zope.interface import implements
from interfaces import ISmartBannerContainerOrdered,ISmartBannerContainerData
from zope.app.container.ordered import OrderedContainer,IOrderedContainer
from zope.app.container.interfaces import IContainer

class SmartBannerContainer( OrderedContainer ) :
    ''' '''
    implements(ISmartBannerContainerOrdered,ISmartBannerContainerData,IContainer)

    use_fake_place = None

    fake_place_root = None
                    
    algorithm = 'Random'