from cool_global import *

def align(n, alignment):
    if n % alignment == 0:
        return n
    return n + (alignment - (n % alignment))

def type2String(ty: 'Type'):
    if ty == integerType:
        return 'Int'
    elif ty == booleanType:
        return 'Bool'
    elif ty == stringType:
        return 'String'
    else:
        return ty


class CGen_scope(object):

    def __init__(self):
        self.table = []

    def enterScope(self):
        self.table.insert(0, dict())

    def existScope(self):
        if not self.table:
            exit("exit scope: can't remove scope from empty symbol table")

        self.table.pop(0)

    def addId(self, id, offset, ty):
        if not self.table:
            exit("add id in scope: can't add in empty symbol table")

        self.table[0][id] = {}
        self.table[0][id]['offset'] = offset
        self.table[0][id]['type'] = ty



    def lookup(self, id, kind):
        if not self.table:
            exit("lookup id in scope: can't lookup in empty symbol table")

        for scope in self.table:
            if id in scope:
                return scope[id][kind]

        return None

    def lookup_offset(self, id):
        return self.lookup(id, 'offset')

    def lookup_type(self, id):
        return self.lookup(id, 'type')

    
        
    
    def lookupLocal(self, id):
        if not self.table:
            exit("lookup id in scope: can't lookup in empty symbol table")

        return self.table[0].get(id, None)

    

