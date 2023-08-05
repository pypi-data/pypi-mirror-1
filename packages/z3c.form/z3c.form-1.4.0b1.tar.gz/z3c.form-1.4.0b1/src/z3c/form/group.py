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
"""Widget Group Implementation

$Id: group.py 77114 2007-06-26 22:35:05Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.interface

from z3c.form import form, interfaces

class Group(form.BaseForm):

    label = None

    def __init__(self, context, request, parentForm):
        self.context = context
        self.request = request
        self.parentForm = self.__parent__ = parentForm

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        for attrName in ('mode', 'ignoreRequest', 'ignoreContext',
                         'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        self.widgets.update()



class GroupForm(object):
    """A mix-in class for add and edit forms to support groups."""

    groups = ()

    def extractData(self):
        '''See interfaces.IForm'''
        data, errors = super(GroupForm, self).extractData()
        for group in self.groups:
            groupData, groupErrors = group.extractData()
            data.update(groupData)
            if groupErrors:
                if errors:
                    errors += groupErrors
                else:
                    errors = groupErrors
        return data, errors

    def applyChanges(self, data):
        '''See interfaces.IEditForm'''
        changed = False
        content = self.getContent()
        form.applyChanges(self, content, data)
        for group in self.groups:
            groupChanged = form.applyChanges(group, content, data)
            changed = changed or groupChanged
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(content))
        return changed

    def update(self):
        '''See interfaces.IForm'''
        self.updateWidgets()
        groups = []
        for groupClass in self.groups:
            group = groupClass(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)
        self.updateActions()
        self.actions.execute()
