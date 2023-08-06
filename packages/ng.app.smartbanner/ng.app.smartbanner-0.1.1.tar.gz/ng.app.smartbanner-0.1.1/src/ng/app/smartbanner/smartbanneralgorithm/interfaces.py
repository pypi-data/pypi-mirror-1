### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.smartbanner.smartbanner package

$Id: interfaces.py 51701 2008-09-13 22:47:48Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51701 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Date, Int, URI

class ISmartBannerAlgorithm(Interface) :
    """ ISmartBannerAlgorithm
    """
    
    def choice() :
        """ Choice one item from container """
