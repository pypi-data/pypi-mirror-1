### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SimpleBannerVocabulary class for the Zope 3 based ng.app.simplebanner package.

$Id: smartbanneralgorithmvocabulary.py 51936 2008-10-23 08:14:17Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51936 $"


from zope.schema.vocabulary import SimpleVocabulary
from zope.app.zapi import  getSiteManager
from interfaces import ISmartBannerAlgorithm
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer

def SmartBannerAlgorithmVocabulary(context):
    return SimpleVocabulary.fromValues(
            [x for x,y in getSiteManager(context).adapters.lookupAll(
                [ISmartBannerContainer], ISmartBannerAlgorithm
                )]
        )
