##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Widget Framework Implementation

$Id: widget.py 76276 2007-06-04 06:45:36Z srichter $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.location
import zope.schema.interfaces
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate

from z3c.form import interfaces, util, value
from z3c.form.i18n import MessageFactory as _

PLACEHOLDER = object()

StaticWidgetAttribute = value.StaticValueCreator(
    discriminators = ('context', 'request', 'view', 'field', 'widget')
    )
ComputedWidgetAttribute = value.ComputedValueCreator(
    discriminators = ('context', 'request', 'view', 'field', 'widget')
    )


class Widget(zope.location.Location):
    """Widget base class."""

    zope.interface.implements(interfaces.IWidget)

    # widget specific attributes
    label = u''
    mode = interfaces.INPUT_MODE
    required = False
    ignoreRequest = False
    ignoreContext = False
    error = None
    template = None
    value = None

    # html element attributes
    id = u''
    name = u''
    title = None
    css = None
    tabindex = None
    disabled = None

    # this is only for a simpler handling, note that we offer interfaces
    # for the following attributes, See IContextAware, IFormAware, IFieldWidget
    context = None
    form = None
    field = None

    def __init__(self, request):
        self.request = request

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Step 1: Determine the value.
        value = interfaces.NOVALUE
        lookForDefault = False
        # Step 1.1: If possible, get a value from the request
        if not self.ignoreRequest:
            widget_value = self.extract()
            if widget_value is not interfaces.NOVALUE:
                # Once we found the value in the request, it takes precendence
                # over everything and nothing else has to be done.
                self.value = widget_value
                value = PLACEHOLDER
        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if (interfaces.IFieldWidget.providedBy(self) and
            value is interfaces.NOVALUE and
            value is not PLACEHOLDER):
            # Step 1.2.1: If the widget knows about its context and the
            #              context is to be used to extract a value, get
            #              it now via a data manager.
            if (interfaces.IContextAware.providedBy(self) and
                not self.ignoreContext):
                value = zope.component.getMultiAdapter(
                    (self.context, self.field), interfaces.IDataManager).get()
            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the field, id set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            if ((value is self.field.missing_value or
                 value is interfaces.NOVALUE) and
                self.field.default is not None):
                value = self.field.default
                lookForDefault = True
        # Step 1.3: If we still have not found a value, then we try to get it
        #           from an attribute value
        if value is interfaces.NOVALUE or lookForDefault:
            adapter = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IValue, name='default')
            if adapter:
                value = adapter.get()
        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (interfaces.NOVALUE, PLACEHOLDER):
            converter = interfaces.IDataConverter(self)
            self.value = converter.toWidgetValue(value)
        # Step 2: Update selected attributes
        for attrName in ('label', 'required'):
            value = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IValue, name=attrName)
            if value is not None:
                setattr(self, attrName, value.get())

    def render(self):
        """See z3c.form.interfaces.IWidget."""
        template = self.template
        if template is None:
            template = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                IPageTemplate, name=self.mode)
        return template(self)

    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        return self.request.get(self.name, default)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class SequenceWidget(Widget):
    """Sequence widget."""

    zope.interface.implements(interfaces.ISequenceWidget)

    value = ()
    terms = None

    noValueToken = '--NOVALUE--'

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                value.append(translate(
                    term.title, context=self.request, default=term.title))
            else:
                value.append(term.token)
        return value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Create terms first, since we need them for the generic update.
        if self.terms is None:
            self.terms = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms)
        super(SequenceWidget, self).update()

    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value


def FieldWidget(field, widget):
    """Set the field for the widget."""
    widget.field = field
    if not interfaces.IFieldWidget.providedBy(widget):
        zope.interface.alsoProvides(widget, interfaces.IFieldWidget)
    # Initial values are set. They can be overridden while updating the widget
    # itself later on.
    widget.name = field.__name__
    widget.id = field.__name__.replace('.', '-')
    widget.label = field.title
    widget.required = field.required
    return widget


class WidgetTemplateFactory(object):
    """Widget template factory."""

    def __init__(self, filename, contentType='text/html',
                 context=None, request=None, view=None,
                 field=None, widget=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(context),
            util.getSpecification(request),
            util.getSpecification(view),
            util.getSpecification(field),
            util.getSpecification(widget))(self)
        zope.interface.implementer(IPageTemplate)(self)

    def __call__(self, context, request, view, field, widget):
        return self.template
