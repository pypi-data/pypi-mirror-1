Package ng.zcmlmultiform short description
==========================================

Package was developed to create content edit multiform by means of several
subform compound. Each subform appointed to edit some of interfaces
content-component.

Subform displayed only when needed interface is provided by component. This
approach allow create universal forms fit to edit large set of component.

The multiform is like to context menu: content chooses automaticaly in
depend from interfaces provided by content. However, using multiform is
rather then menu, because of clicks number is fewer.

            
Directive definitions
----------------------

Package introduce two directives: multiform and multiformitem, relations beetween
ones is like on menu and menuitem directives. Multiform define place for content,
Multiform item define content.



multiform
~~~~~~~~~

The directive allow to define multiform created from several simple form.
Binding form and multiform is defined by means of interfaces entered in
manager fields of both directive multiform and multiformitem. It's to be
equal or have some level affinity.

 name : TextLine 
    Name of multiform page in web
    
 permission : Permission
    The permission needed to use the view of forms.
    
 class  : GlobalObject 
    Mix-In class supplied helper attributes and methods for the multiform view .
    
 
 for : GlobalObject 
    The interface or class this multifirm view is for.

 label : MessageID 
    The title of multiform.

 layer : GlobalInterface
    The skin the view is in.

 manager : GlobalObject 
    Interface used to bound page and forms contents from.

 menu : MenuField 
    The browser menu to include the page (view) in.  Many views are included
    in menus. It's convenient to name the menu in the page directive, rather
    than having to give a separate menuItem directive.

 template : Path (по умолчанию = None)
    Page template Refers to a file containing a page template (should end in
    extension `.pt` or `.html`).

 title : MessageID
    The browser menu label for the page (view) This attribute must be
    supplied if a menu attribute is supplied.

mulltiformitem
~~~~~~~~~~~~~~

The directive used to define multiform item.

 permission : Permission
    The permission needed to use the view of forms.

 schema : GlobalInterface
    The schema from which the form is generated.

 class : GlobalObject 
    Mix-In class supplied helper attributes and methods for the form.
    

 for : GlobalObject 
    The interface or class this form is for.
    
    
 layer : GlobalInterface 
    The skin the view is in.


 manager : GlobalObject
    Interface used to bound page and forms contents from.

 name : TextLine (по умолчанию = None)
    Name of form, used to distinguish form in inner presentation algorithm.

 order : Int (по умолчанию = None)
    Form order
    
 template : Path 
    Form template. Refers to a file containing a template (should end in
    extension `.pt` or `.html`).

 fields : Tokens
    List of fields to display in form item.

Subdirective widget
...................

Register custom widgets for a form.  This directive allows you to
quickly generate custom widget directives for a form.  Besides the two
required arguments, field and class, you can specify any amount of
keyword arguments, e.g. style='background-color:#fefefe;'. The keywords
will be stored as attributes on the widget instance. To see which
keywords are sensible, you should look at the code of the specified
widget class.

 field : TextLine 
    Field Name, The name of the field/attribute/property for which this
    widget will be used.
    
 class : GlobalObject 
    Widget Class. The class that will create the widget.

