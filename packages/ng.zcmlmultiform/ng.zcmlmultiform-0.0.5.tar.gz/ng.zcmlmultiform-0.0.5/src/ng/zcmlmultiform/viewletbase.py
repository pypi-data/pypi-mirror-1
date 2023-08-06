# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbase.py 50197 2008-01-20 20:25:07Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50197 $"

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
        