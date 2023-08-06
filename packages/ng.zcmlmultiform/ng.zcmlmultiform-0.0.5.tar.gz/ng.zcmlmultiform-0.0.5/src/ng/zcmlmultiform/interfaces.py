### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 50167 2008-01-19 12:36:28Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 50167 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
                
class IMultiFormManager(Interface) :
    pass
                            
                            