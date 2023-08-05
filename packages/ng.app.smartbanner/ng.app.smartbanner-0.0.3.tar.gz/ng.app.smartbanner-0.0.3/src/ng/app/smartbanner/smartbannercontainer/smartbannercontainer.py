### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: smartbannercontainer.py 49685 2008-01-23 14:31:46Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49685 $"

from zope.interface import implements
from interfaces import ISmartBannerContainerOrdered,ISmartBannerContainerData
from zope.app.container.ordered import OrderedContainer,IOrderedContainer
from zope.app.container.interfaces import IContainer

class SmartBannerContainer( OrderedContainer ) :
    ''' '''
    implements(ISmartBannerContainerOrdered,ISmartBannerContainerData,IContainer)

    use_fake_place = None

    fake_place_root = None
                    
