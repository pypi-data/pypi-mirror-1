### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ZCML Multiform directive handler

$Id: metaconfigure.py 51412 2008-07-18 15:27:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51412 $"
 
from zope.app.form.browser.metaconfigure import EditFormDirectiveBase
from zope.viewlet.metaconfigure import viewletDirective, viewletManagerDirective
from multiformitem import MultiFormItemView
from multiform import MultiFormView
from ng.zcmlmultiform import default_template_path,default_multitemplate_path
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from zope.app.publisher.browser.viewmeta import page
from interfaces import IMultiFormManager

class FormDirective(EditFormDirectiveBase) :
    default_template = 'multiformitem.pt'

    view = MultiFormItemView
    def __init__(self, _context, fields=[], **kwargs) :
        
        if fields :
          class A(self.view) :
              fieldNames = fields
            
          self.view = A
        super(FormDirective,self).__init__(_context,fields=fields,**kwargs)
    
    def __call__(self) :
        self._processWidgets()
        if self.template == self.default_template :
            self.template = default_template_path
        return viewletDirective(
            self._context, 
            self.name, self.permission,
            for_=self.for_,
            layer=self.layer, 
            # view=IBrowserView, ????
            manager=self.manager,
            class_=self.view,
            template=self.template,
            schema=self.schema,
            order=self.order,
            prefix=self.name,
            )

def ids() :
    i = 0
    while True :
        i+=1
        yield "multiformprovider-%03u" % i    

ids = ids().next

def MultiFormDirective(_context, name, permission, manager = IMultiFormManager, template= None,
    class_= None, for_ = Interface, label=u"", layer = IDefaultBrowserLayer, provides=IMultiFormManager, menu=None, title=None ) :

    providername = ids()    
    viewletManagerDirective(_context, providername, permission, for_=for_, layer=layer, provides=manager)
    if template == None :
        template = default_multitemplate_path

    if class_ is None :
        bases = (MultiFormView,)
    else :
        bases = (MultiFormView, class_)
        
    page(_context, name, permission, for_ = for_, layer=layer,
        template=template, menu=menu, title=title,
        class_=type("Next", bases, { 
            'providername' : providername,
            'label' : label,
            'if1' : IBrowserView,
            'if2' : manager,
        }) )

