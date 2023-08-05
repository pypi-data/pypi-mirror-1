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
"""Utilities helpful to the package.

$Id: util.py 75940 2007-05-24 14:45:00Z srichter $
"""
__docformat__ = "reStructuredText"
import re
import types
import zope.interface

from z3c.form import interfaces


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')

def createId(name):
    if _identifier.match(name):
        return str(name).lower()
    return name.encode('hex')


classTypes = type, types.ClassType

def getSpecification(spec, force=False):
    """Get the specification of the given object.

    If the given object is already a specification acceptable to the component
    architecture, it is simply returned. This is true for classes
    and specification objects (which includes interfaces).

    In case of instances, an interface is generated on the fly and tagged onto
    the object. Then the interface is returned as the specification.
    """
    # If the specification is an instance, then we do some magic.
    if (force or
        (spec is not None and
         not zope.interface.interfaces.ISpecification.providedBy(spec)
         and not isinstance(spec, classTypes)) ):
        # Step 1: Create an interface
        iface = zope.interface.interface.InterfaceClass(
            'IGeneratedForObject_%i' %hash(spec))
        # Step 2: Directly-provide the interface on the specification
        zope.interface.alsoProvides(spec, iface)
        # Step 3: Make the new interface the specification for this instance
        spec = iface
    return spec


def expandPrefix(prefix):
    """Expand prefix string by adding a trailing period if needed.

    expandPrefix(p) should be used instead of p+'.' in most contexts.
    """
    if prefix and not prefix.endswith('.'):
        return prefix + '.'
    return prefix


def getWidgetById(form, id):
    """Get a widget by it's rendered DOM element id."""
    prefix = form.prefix + form.widgets.prefix
    if not id.startswith(prefix):
        raise ValueError("Id %r must start with prefix %r" %(id, prefix))
    shortName = id[len(prefix):]
    return form.widgets.get(shortName, None)


class Manager(object):
    """Non-persistent IManager implementation."""
    zope.interface.implements(interfaces.IManager)

    def __init__(self, *args, **kw):
        self._data_keys = []
        self._data_values = []
        self._data = {}

    def __len__(self):
        return len(self._data_values)

    def __iter__(self):
        return iter(self._data_keys)

    def __getitem__(self, name):
        return self._data[name]

    def get(self, name, default=None):
        return self._data.get(name, default)

    def keys(self):
        return self._data_keys

    def values(self):
        return self._data_values

    def items(self):
        return [(i, self._data[i]) for i in self._data_keys]

    def __contains__(self, name):
        return bool(self.get(name))


class SelectionManager(Manager):
    """Non-persisents ISelectionManager implementation."""
    zope.interface.implements(interfaces.ISelectionManager)

    managerInterface = None

    def __add__(self, other):
        if not self.managerInterface.providedBy(other):
            return NotImplemented
        return self.__class__(self, other)

    def select(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(
            *[item for item in self.values()
              if item.__name__ not in names])

    def copy(self):
        """See interfaces.ISelectionManager"""
        return self.__class__(*self.values())
