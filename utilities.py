def align(n, alignment):
    if n % alignment == 0:
        return n
    return n + (alignment - (n % alignment))


class CGen_scope(object):

    def __init__(self):
        self.table = []

    def enterScope(self):
        self.table.insert(0, dict())

    def existScope(self):
        if not self.table:
            exit("exit scope: can't remove scope from empty symbol table")

        self.table.pop(0)

    def addId(self, id, offset):
        if not self.table:
            exit("add id in scope: can't add in empty symbol table")

        self.table[0][id] = offset

    def lookup(self, id):
        if not self.table:
            exit("lookup id in scope: can't lookup in empty symbol table")

        for scope in self.table:
            if id in scope:
                return scope[id]

        return None
        
    
    def lookupLocal(self, id):
        if not self.table:
            exit("lookup id in scope: can't lookup in empty symbol table")

        return self.table[0].get(id, None)

    

