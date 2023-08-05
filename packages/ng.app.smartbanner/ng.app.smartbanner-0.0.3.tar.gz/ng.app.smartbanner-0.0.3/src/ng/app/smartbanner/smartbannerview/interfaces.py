### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based smartbannerview package

$Id: interfaces.py 49685 2008-01-23 14:31:46Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49685 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
