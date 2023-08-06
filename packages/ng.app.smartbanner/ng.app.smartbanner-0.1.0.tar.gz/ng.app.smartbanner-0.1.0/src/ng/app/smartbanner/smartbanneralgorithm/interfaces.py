### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.smartbanner.smartbanner package

$Id: interfaces.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Date, Int, URI

class ISmartBannerAlgorithm(Interface) :
    """ ISmartBannerAlgorithm
    """
    
    def choice() :
        """ Choice one item from container """
