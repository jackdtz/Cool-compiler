from cool_types import *
import cool_global as GLOBAL


class Scope(object):


    def __init__(self, enclosingClass: Type=None, parent: 'Scope'=None):
        """
        takes in a type that represented the class that enclose the current scope, 
        and another scope represented the parent scope. The constructor also initialize 
        an empty hash table, as well as an reference to the scope of the parent class of 
        current enclosing class type
        """
        self.parentScope = parent
        self.enclosingClass = enclosingClass
        self.inheritClassScope = None
        self.table = {}

    def add(self, key, value, ty):
        """
        each key has two information associated to it: a type info, and a value info.
        """
        self.table[key] = {}
        self.table[key]['type'] = ty
        self.table[key]['value'] = value

    def delete(self, key):
        """
        delete a key and its associated information
        """
        del self.table[key]

    def lookup(self, key):
        """
        takes in a key and return its value information
        """
        return self.lookupProperty(key, 'value')

    def lookupType(self, key):
        """
        takes in a key and return its type information
        """
        return self.lookupProperty(key, 'type')

    def lookupLocal(self, key):
        """
        takes in a key and lookup its value information at the current scope
        """
        return self.lookupProperty(key, 'value')

    def lookupLocalType(self, key):
        """
        takes in a key and lookup its type information at the current scope
        """
        return self.lookupPropertyLocal(key, 'type')

    def lookupPropertyLocal(self, key, kind):
        """
        takes in a key and lookup its information at the current scope
        """
        val = self.table.get(key, None)

        if val:
            return val[kind]

        return None

    def lookupProperty(self, key, kind):
        """
        lookup in the scope environment
        """
        val = self.lookupPropertyLocal(key, kind)

        if val:
            return val

        s = self
        while s.parentScope and not val:
            s = s.parentScope
            val = s.lookupPropertyLocal(key, kind)

        if val:
            return val

        if self.inheritClassScope:
            return self.inheritClassScope.lookupProperty(key, kind)

        return None

    def getDefiningScope(self, name: str) -> 'Scope':
        """
        Provided a name, return the scope at which it is defined.
        """
        ret = self.table.get(name, None)

        if ret:
            return ret['value']
        elif self.parentScope:
            return self.parentScope.getDefiningScope(name)
        else:
            return None

    def getEnclosingClassScope(self) -> 'Scope':
        """
        return the class-level scope that enclose the current scope
        """
        s = self
        while s.parentScope.enclosingClass != GLOBAL.topLevelClass:
            s = s.parentScope

        return s

    def getTopLevelScope(self) -> 'Scope':
        """
        return the top-level scope
        """
        s = self
        while s.enclosingClass != GLOBAL.topLevelClass:
            s = s.parentScope
        return s

    def openscope(self, name: str, ty: 'Type', selfclass=None):
        newscope = Scope(parent=self)
        newscope.inheritClassScope = self.inheritClassScope
        if not selfclass:
            newscope.enclosingClass = self.enclosingClass
        else:
            newscope.enclosingClass = selfclass

        self.table[name] = {
            'type': ty,
            'value': newscope
        }

        return newscope

    def leavescope(self):
        return self.parentScope

    @staticmethod
    def initTopScope(scope):
        """
        initialize the top-level scope
        """
        object_scope = Scope(parent=scope)
        object_scope.add('abort', None, FuncType([], GLOBAL.objectType))
        object_scope.add('type_name', None, FuncType([], GLOBAL.stringType))
        object_scope.add('copy', None, FuncType([], GLOBAL.selfType))
        scope.add('Object', object_scope, GLOBAL.objectType)

        string_scope = Scope(parent=scope)
        string_scope.inheritClassScope = object_scope
        string_scope.enclosingClass = GLOBAL.topLevelClass
        string_scope.add('length', None, FuncType([], GLOBAL.integerType))
        string_scope.add('concat', None, FuncType(
            [GLOBAL.stringType], GLOBAL.stringType))
        string_scope.add('substr', None, FuncType(
            [GLOBAL.integerType, GLOBAL.integerType], GLOBAL.stringType))
        scope.add('String', string_scope, GLOBAL.stringType)

        io_scope = Scope(parent=scope)
        io_scope.inheritClassScope = object_scope
        io_scope.enclosingClass = GLOBAL.topLevelClass
        io_scope.add('out_string', None, FuncType(
            [GLOBAL.stringType], GLOBAL.selfType))
        io_scope.add('out_int', None, FuncType(
            [GLOBAL.integerType], GLOBAL.selfType))
        io_scope.add('in_string', None, FuncType([], GLOBAL.stringType))
        io_scope.add('in_int', None, FuncType([], GLOBAL.integerType))
        scope.add('IO', io_scope, ClassType("IO", parent=GLOBAL.objectType))

        boolean_scope = Scope(parent=scope)
        boolean_scope.inheritClassScope = object_scope
        boolean_scope.enclosingClass = GLOBAL.topLevelClass
        scope.add('Bool', boolean_scope, GLOBAL.booleanType)

        int_scope = Scope(parent=scope)
        int_scope.inheritClassScope = object_scope
        int_scope.enclosingClass = GLOBAL.topLevelClass
        scope.add('Int', int_scope, GLOBAL.integerType)



    def findScopeByType(self, topScope: 'Scope', ty: 'Type') -> 'Scope':
        """
        Provide a type object (note that every type object is unique) and return its associate scope.
        """
        for k, v in topScope.table.items():
            if v['type'] == ty:
                return v['value']

        return None


