### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannercontainer.py 51701 2008-09-13 22:47:48Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51701 $"

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