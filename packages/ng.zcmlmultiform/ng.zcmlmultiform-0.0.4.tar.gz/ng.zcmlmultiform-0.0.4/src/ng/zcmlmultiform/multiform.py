### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Mix-in class for use in multiform item class.

$Id: multiform.py 51584 2008-08-31 14:51:11Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51584 $"

from zope.viewlet.interfaces import IViewlet
from zope.component import getAdapters, queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

class MultiFormView(object) :
    errors = []
    def update_form(self) :
        provider = queryMultiAdapter(
            (self.context, self.request, self), IContentProvider, self.providername)            
        viewlets = getAdapters( (self.context, self.request, self, provider), IViewlet)
        ls = []
        errors = []
        for name,viewlet in provider.filter(viewlets) :
            s = viewlet.update_form()
            ls.append(s)
            errors.extend(viewlet.errors)

        self.errors = errors
        return "\n".join(ls)        
        