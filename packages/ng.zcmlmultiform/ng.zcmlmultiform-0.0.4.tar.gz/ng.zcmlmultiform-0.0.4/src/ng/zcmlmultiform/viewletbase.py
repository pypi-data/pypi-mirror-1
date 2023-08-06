# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbase.py 51584 2008-08-31 14:51:11Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51584 $"

class ViewletBase(object) :
    """ Body """

    order = 0 
    
    def __init__(self,context,request,*kv,**kw) :
        self.context = context
        self.request = request
        self.order = int(str(self.order))
        super(ViewletBase,self).__init__(context,request,*kv,**kw)

    def __cmp__(self,x) :
        return cmp(int(str(self.order)),int(str(x.order)))
        