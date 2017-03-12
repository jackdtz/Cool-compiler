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
        self.inheritClassScope = None
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
        return self.lookupPropertyLocal(key, 'type')

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
            val = s.lookupPropertyLocal(key, kind)

        if val:
            return val

        if self.inheritClassScope:
            return self.inheritClassScope.lookupProperty(key, kind)

        return None

    def getDefiningScope(self, name : str) -> 'Scope':
        ret = self.table.get(name, None)

        if ret:
            return ret['value']
        elif self.parent:
            return self.parent.getDefiningScope(name)
        else:
            return None

    def getEnclosingClassScope(self) -> 'Scope':
        s = self
        while s.parent.enclosingClass != GLOBAL.topLevelClass:
            s = s.parent

        return s

    def getTopLevelScope(self) -> 'Scope':
        s = self
        while s.enclosingClass != GLOBAL.topLevelClass:
            s = s.parent
            if not s:
                print("haha")
        return s
            


    def openscope(self, name : str, ty : 'Type', selfclass=None):
        newscope = Scope(parent=self)
        newscope.inheritClassScope = self.inheritClassScope
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

    @staticmethod
    def initTopScope(scope):
        io_scope = Scope(parent=scope)
        io_scope.add('out_string', None, FuncType([GLOBAL.stringType], GLOBAL.selfType))
        io_scope.add('out_int', None, FuncType([GLOBAL.integerType], GLOBAL.selfType))
        io_scope.add('in_string', None, FuncType([], GLOBAL.stringType))
        io_scope.add('in_int', None, FuncType([], GLOBAL.integerType))
        scope.add('IO', io_scope, ClassType(parent=GLOBAL.objectType))

        object_scope = Scope(parent=scope)
        object_scope.add('abort', None, FuncType([], GLOBAL.objectType))
        object_scope.add('type_name', None, FuncType([], GLOBAL.stringType))
        object_scope.add('copy', None, FuncType([], GLOBAL.selfType))
        scope.add('Object', object_scope, GLOBAL.objectType)

        string_scope = Scope(parent=scope)
        string_scope.add('length', None, FuncType([], GLOBAL.integerType))
        string_scope.add('concat', None, FuncType([GLOBAL.stringType], GLOBAL.stringType))
        string_scope.add('substr', None, FuncType([GLOBAL.integerType, GLOBAL.integerType], GLOBAL.stringType))
        scope.add('String', string_scope, GLOBAL.stringType)

    def findScopeByType(self, topScope: 'Scope', ty: 'Type') -> 'Scope':
        for k, v in topScope.table.items():
            if v['type'] == ty:
                return v['value'] 

        return None

