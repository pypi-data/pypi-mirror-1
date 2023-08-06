# Copyright 2008 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.delegates.
#
# lazr.delegates is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.delegates is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.delegates.  If not, see <http://www.gnu.org/licenses/>.

"""Decorator helpers that simplify class composition."""


__metaclass__ = type


__all__ = ['delegates', 'Passthrough']


import sys
from types import ClassType

from zope.interface.advice import addClassAdvisor
from zope.interface import classImplements


def delegates(interface, context='context'):
    """Make an adapter into a decorator.

    Use like:

        class RosettaProject:
            implements(IRosettaProject)
            delegates(IProject)

            def __init__(self, context):
                self.context = context

            def methodFromRosettaProject(self):
                return self.context.methodFromIProject()

    If you want to use a different name than "context" then you can explicitly
    say so:

        class RosettaProject:
            implements(IRosettaProject)
            delegates(IProject, context='project')

            def __init__(self, project):
                self.project = project

            def methodFromRosettaProject(self):
                return self.project.methodFromIProject()

    The adapter class will implement the interface it is decorating.

    The minimal decorator looks like this:

    class RosettaProject:
        delegates(IProject)

        def __init__(self, context):
            self.context = context

    """
    # pylint: disable-msg=W0212
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a class def
    if (locals is frame.f_globals) or ('__module__' not in locals):
        raise TypeError(
            "delegates() can be used only from a class definition.")

    locals['__delegates_advice_data__'] = interface, context
    addClassAdvisor(_delegates_advice, depth=2)


def _delegates_advice(cls):
    """Add a Passthrough class for each missing interface attribute.

    This function connects the decorator class to the delegate class.
    Only new-style classes are supported.
    """
    interface, contextvar = cls.__dict__['__delegates_advice_data__']
    del cls.__delegates_advice_data__
    if type(cls) is ClassType:
        raise TypeError(
            'Cannot use delegates() on a classic class: %s.' % cls)
    classImplements(cls, interface)
    for name in interface:
        if not hasattr(cls, name):
            setattr(cls, name, Passthrough(name, contextvar))
    return cls


class Passthrough:
    """Call the delegated class for the decorator class."""
    def __init__(self, name, contextvar):
        self.name = name
        self.contextvar = contextvar

    def __get__(self, inst, cls=None):
        if inst is None:
            return self
        else:
            return getattr(getattr(inst, self.contextvar), self.name)

    def __set__(self, inst, value):
        setattr(getattr(inst, self.contextvar), self.name, value)

    def __delete__(self, inst):
        raise NotImplementedError
