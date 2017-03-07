from collections import OrderedDict
import sys
from cool_types import *


class Scope(object):
    """
    each scope in a hash table
    """

    def __init__(self, selfclass: Type=None, parent: Type=None):
        self.parent = parent
        self.selfclass = selfclass
        self.ttable = {}
        self.vtable = {}

    def copy(self) -> 'Scope':
        newScope = Scope(selfclass=self.selfclass, parent=self.parent)

        for key, val in self.ttable.items():
            newScope.ttable[key] = val

        for key, val in self.vtable.items():
            newScope.vtable[key] = val
        return newScope

    def vadd(self, key, value):
        self.vtable[key] = value

    def tadd(self, key, value):
        self.ttable[key] = value

    def vlookup(self, key, scope=None):
        """
        lookup in the value environment
        """
        val = self.vtable.get(key, None)

        if val:
            return val

        s = self
        while s.parent and not val:
            s = s.parent
            val = s.lookup(key)

        if not val:
            print("Undefined val {}".format(str(key)))
            return

        return val

    def tlookup(self, key, scope: 'Scope') -> Type:
        """
        lookup in the type environment
        """
        pass

    @staticmethod
    def openscope(parent=None, selfclass=None):
        newscope = Scope(parent=parent)
        if not selfclass:
            newscope.selfclass = parent.selfclass
        else:
            newscope.selfclass = selfclass
        return newscope
