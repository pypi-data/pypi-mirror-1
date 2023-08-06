### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SimpleBannerVocabulary class for the Zope 3 based ng.app.simplebanner package.

$Id: smartbanneralgorithmvocabulary.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"


from zope.schema.vocabulary import SimpleVocabulary
from zope.app.zapi import getUtilitiesFor, getAdapters
from interfaces import ISmartBannerAlgorithm

def SmartBannerAlgorithmVocabulary(context):
    return SimpleVocabulary.fromValues([x for x,y in getAdapters([context], ISmartBannerAlgorithm, context=context)])
