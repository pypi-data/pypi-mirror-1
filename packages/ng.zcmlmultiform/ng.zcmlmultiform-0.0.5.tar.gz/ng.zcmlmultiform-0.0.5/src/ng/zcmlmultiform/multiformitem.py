### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Mix-in class for use in multiform item class.

$Id: multiformitem.py 52661 2009-03-04 11:34:36Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52661 $"

from interfaces import Interface
from viewletbase import ViewletBase
from zope.app.form.browser.editview import EditView
from zope.schema import getFieldsInOrder, getFieldNames
from zope.viewlet.viewlet import simple
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class MultiFormItemView(EditView,simple,ViewletBase) :
    """ MultiFromView """
    schema = Interface
    prefix = "dict"
    default_template = 'multiformitem.pt'
    generated_form = ViewPageTemplateFile(default_template)

    def __init__(self,context,request,*kv,**kw) :
        #fieldNames = getFieldNames(self.schema)
        super(simple,self).__init__(context,request,*kv,**kw)
        self._setUpWidgets()
        self.setPrefix(self.prefix)
        
    def update(self) :
        pass

    def update_form(self) :
        return EditView.update(self)
