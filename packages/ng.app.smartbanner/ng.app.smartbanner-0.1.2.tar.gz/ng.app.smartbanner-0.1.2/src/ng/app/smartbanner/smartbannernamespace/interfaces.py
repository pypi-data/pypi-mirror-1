### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51936 2008-10-23 08:14:17Z cray $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51936 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.file.interfaces import IImage
from zope.schema import TextLine
                


