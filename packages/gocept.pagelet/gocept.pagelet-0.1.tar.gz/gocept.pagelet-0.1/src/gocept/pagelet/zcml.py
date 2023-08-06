# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: zcml.py 5286 2007-10-15 10:57:46Z zagy $

import zope.configuration.fields
import zope.interface
import zope.publisher.interfaces.browser
import zope.viewlet.metaconfigure

import zope.app.publisher.browser.fields
import zope.app.publisher.browser.viewmeta

import z3c.pagelet.browser
import z3c.pagelet.interfaces
import z3c.pagelet.zcml
import z3c.template.zcml

import gocept.pagelet.viewletpage


class IPageletDirective(z3c.pagelet.zcml.IPageletDirective):
    """A directive to easiliy register a new pagelet with a layout tempalte.

    """

    class_ = zope.configuration.fields.GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the pagelet.",
        required=False,
        )

    template = zope.configuration.fields.Path(
        title=u'Layout template.',
        description=u"Refers to a file containing a page template (should "
                     "end in extension ``.pt`` or ``.html``).",
        required=False,
        )

    title = zope.configuration.fields.MessageID(
        title=u"The browser menu label for the page (view)",
        description=u"""
          This attribute must be supplied if a menu attribute is
          supplied.
          """,
        required=False
        )
   
    menu = zope.app.publisher.browser.fields.MenuField(
        title=u"The browser menu to include the page (view) in.",
        description=u"""
          Many views are included in menus. It's convenient to name
          the menu in the page directive, rather than having to give a
          separate menuItem directive.  'zmi_views' is the menu most often
          used in the Zope management interface.
          </description>
          """,
        required=False
        )

def pageletDirective(
    _context, name, permission, class_=None, for_=zope.interface.Interface,
    layer=zope.publisher.interfaces.browser.IDefaultBrowserLayer,
    allowed_interface=None, allowed_attributes=None, template=None,
    title=None, menu=None,
    **kwargs):

    if class_:
        new_class = class_
    else:
        new_class = type('SimplePagelet', (object, ), {})

    z3c.pagelet.zcml.pageletDirective(
        _context, new_class, name, permission,
        for_=for_, layer=layer,
        allowed_interface=allowed_interface,
        allowed_attributes=allowed_attributes)

    if template:
        z3c.template.zcml.templateDirective(
            _context, template, for_=new_class, layer=layer)

    zope.app.publisher.browser.viewmeta._handle_menu(
        _context, menu, title, [for_], name, permission, layer)


class ViewletPageDirective(object):

    def __init__(self, _context, name, permission,
                 class_=gocept.pagelet.viewletpage.ViewletPage,
                 **kwargs):
        self._context = _context
        self.name = name
        self.permission = permission
        self.class_ = class_
        self.kwargs = kwargs

    def __call__(self):
        z3c.pagelet.zcml.pageletDirective(
            self._context, self.class_, self.name, self.permission,
            **self.kwargs)

    def viewlet(self, _context, name, permission, layer=None, **kwargs):
        kwargs["manager"] = gocept.pagelet.viewletpage.IViewletPageManager
        zope.viewlet.metaconfigure.viewletDirective(
            _context, name, permission,
            layer=layer or self.kwargs.get("layer"),
            **kwargs)
