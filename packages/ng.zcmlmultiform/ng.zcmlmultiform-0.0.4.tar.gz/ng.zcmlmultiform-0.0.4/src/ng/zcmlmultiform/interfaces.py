### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51584 2008-08-31 14:51:11Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 51584 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
                
class IMultiFormManager(Interface) :
    pass
                            
                            