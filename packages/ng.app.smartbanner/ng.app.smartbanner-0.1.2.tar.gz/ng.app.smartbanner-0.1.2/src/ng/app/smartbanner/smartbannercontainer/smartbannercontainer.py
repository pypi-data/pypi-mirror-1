### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannercontainer.py 51936 2008-10-23 08:14:17Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51936 $"

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