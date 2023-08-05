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
"""Text Widget Implementation

$Id: text.py 75940 2007-05-24 14:45:00Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces, widget


class TextWidget(widget.Widget):
    """Input type text widget implementation."""

    zope.interface.implementsOnly(interfaces.ITextWidget)

    css = u'textWidget'
    size = None
    value = u''

    # optional html attributes
    alt = None
    readonly = None
    maxlength = None
    accesskey = None


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def TextFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return widget.FieldWidget(field, TextWidget(request))
