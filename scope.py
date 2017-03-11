from collections import OrderedDict
import sys
from cool_types import *
import copy
import cool_global as GLOBAL


class Scope(object):
    """
    each scope in a hash table
    """

    def __init__(self, enclosingClass: Type=None, parent: Type=None):
        self.parent = parent
        self.enclosingClass = enclosingClass
        self.table = {}

    def copy(self) -> 'Scope':
        return copy.deepcopy(self)

    def add(self, key, value, ty):
        self.table[key] = {}
        self.table[key]['type'] = ty
        self.table[key]['value'] = value

    def lookup(self, key):
        return self.lookupProperty(key, 'value')

    def lookupType(self, key):
        return self.lookupProperty(key, 'type')

    def lookupLocal(self, key):
        """
        return either None or the value associated to key
        """
        return self.lookupProperty(key, 'value')

    def lookupLocalType(self, key):
        """
        return either None or the type associated to key
        """
        return self.lookupProperty(key, 'type')

    def lookupPropertyLocal(self, key, kind):
        val = self.table.get(key, None)

        if val:
            return val[kind]

        return None

    def lookupProperty(self, key, kind):
        """
        lookup in the value environment
        """
        val = self.lookupPropertyLocal(key, kind)

        if val:
            return val

        s = self
        while s.parent and not val:
            s = s.parent
            val = s.lookupPropertyLocal(key)

        if not val:
            return None

        return val

    def getDefiningScope(self, name : str) -> 'Scope':
        ret = self.table.get(name, None)

        if ret:
            return ret
        elif self.parent:
            return self.parent.getDefiningScope(name)
        else:
            return None

    def getEnclosingClassScope(self) -> 'Scope':
        s = self
        while s.parent.enclosingClass != GLOBAL.topLevelClass:
            s = s.parent

        return s
            


    def openscope(self, name : str, ty : 'Type', selfclass=None):
        newscope = Scope(parent=self)
        if not selfclass:
            newscope.enclosingClass = self.enclosingClass
        else:
            newscope.enclosingClass = selfclass

        self.table[name] = {
            'type' : ty,
            'value' : newscope
        }

        return newscope

    def leavescope(self):
        return self.parent
