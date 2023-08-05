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
"""Password Widget Implementation

$Id: password.py 300 2007-05-21 15:41:21Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces, widget
from z3c.form.browser import text

class PasswordWidget(text.TextWidget):
    """Input type password widget implementation."""
    zope.interface.implementsOnly(interfaces.IPasswordWidget)

    css = u'passwordWidget'


@zope.component.adapter(zope.schema.interfaces.IPassword, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def PasswordFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return widget.FieldWidget(field, PasswordWidget(request))
