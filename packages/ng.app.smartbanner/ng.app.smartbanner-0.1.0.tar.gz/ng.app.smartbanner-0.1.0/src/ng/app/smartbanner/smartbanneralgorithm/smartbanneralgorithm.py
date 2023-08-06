### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Algortihms Used to select current banner for the
Zope 3 based ng.app.smartbanner package

$Id: smartbanneralgorithm.py 51641 2008-09-06 18:47:13Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51641 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ISmartBannerAlgorithm
from zope.component import adapts
from ng.app.smartbanner.smartbannercontainer.interfaces import ISmartBannerContainer
from random import shuffle, randint
from thread import allocate_lock

class SmartBannerAlgorithmBase(object) :

    implements(ISmartBannerAlgorithm)
    adapts(ISmartBannerContainer)
    
    def __init__(self, context) :
        self.context = context

    def values(self) :
        return (x for x in self.context.values() if x.filter())

    def choice(self) :
        """ Choice one banner
        """

class SmartBannerAlgorithmRandom(SmartBannerAlgorithmBase) :

    def choice(self) :
        """ Choice one banner by simpler random way """
        imgs = []
        sum = 0
        for img in self.values() :
            imgs.append(img)
            sum += img.rate
        
        rnd = randint(0,sum-1)
        pos = 0
        for img in imgs :
            pos += img.rate 
            if pos > rnd :
                break
        return img

class SmartBannerAlgorithmRound(SmartBannerAlgorithmBase) :

    queue = []

    lock = allocate_lock()

    def choice(self) :
        """ Choice one banner by simpler random way """
        self.lock.acquire()
        while True :
            try :
                img = self.queue.pop()
                self.lock.release()
                return img
            except IndexError :
                for img in self.values() :
                    self.queue.extend([img] * int(img.rate))
                shuffle(self.queue)
                        
