### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interface of ZCML metadirectives  for multiform package

$Id: metadirectives.py 51410 2008-07-18 13:59:31Z cray $
"""
__author__  = "AndreyOrlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51410 $"
 
from zope.interface import Interface
from interfaces import IMultiFormManager
from zope.configuration.fields import Path, GlobalObject, GlobalInterface, MessageID, Tokens, PythonIdentifier
from zope.app.publisher.browser.fields import MenuField
from zope.security.zcml import Permission
from zope.schema import TextLine, Int
from interfaces import IMultiFormManager

_ = lambda x : x

class IFormDirective(Interface) :
    manager = GlobalObject(
        title=_(u"view"),
        description=u"The interface of the view this viewlet is for. ",
        required=False,
        default=IMultiFormManager)
    
    name = TextLine(
        title=u"Name", 
        description=u"Name of multiform item", 
        required=False)
    
    class_= GlobalObject(
        title=_(u"Class"),
        description=u"Mix-In class for EditletItem",
        required=False
        )
    
    template=Path(
        title=_(u"Page template"),
        description=_(u"Refers to a file containing a page template (should "
            "end in extension `.pt` or `.html`)."),
        required=False)
    
    layer= GlobalInterface(
        title=_(u"The layer the view is in."),
        description=_(u"""
            skin is composed of layers. It is common to put skin
            specific views in a layer named after the skin. If the 'layer'
            attribute is not supplied, it defaults to 'default'."""),
            required=False,
            )
                                                            
    order=Int(title=u"Item Order",required=False)
    
    schema=GlobalInterface(
        title=u"Schema",
        description=u"The schema from which the form is generated.",
        required=True)
    
    for_ = GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=True
    )
                                                                   
    fields = Tokens(
        title=u"Fields",
        required=False,
        value_type=PythonIdentifier()
    )
    
class IMultiFormDirective(Interface) :

    name = TextLine(title=u"Page name")
    
    manager = GlobalObject(
        title=_(u"view"),
        description=u"The interface of the view this viewlet is for. ",
        required=False,
        default=IMultiFormManager)
    
    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=True)

    template=Path(
        title=_(u"Page template"),
        description=_(u"Refers to a file containing a page template (should "
            "end in extension `.pt` or `.html`)."),
        required=False)

    class_= GlobalObject(
        title=_(u"Class"),
        description=u"Mix-In class for EditletItem",
        required=False
        )
    
    for_ = GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )
    
    layer= GlobalInterface(
        title=_(u"The layer the view is in."),
        description=_(u"""
            skin is composed of layers. It is common to put skin
            specific views in a layer named after the skin. If the 'layer'
            attribute is not supplied, it defaults to 'default'."""),
            required=False,
            )

    menu = MenuField(
        title=u"The browser menu to include the page (view) in.",
        description=u"""
        Many views are included in menus. It's convenient to name the
        menu in the page directive, rather than having to give a
        separate menuItem directive.""",
        required=False
        )

    title = MessageID(
        title=u"The browser menu label for the page (view)",
        description=u"""
        This attribute must be supplied if a menu attribute is
        supplied.""",
        required=False
        )

    label = MessageID(
        title=u"The title of view page",
        required=False
        )

                                                               
                                                               