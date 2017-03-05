from collections import OrderedDict




class Scope(object):
    """
    each scope in a hash table
    """


    def __init__(self, parent=None):
        self.parent = parent
        self.table = {}

        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0


    def copy(self):
        newtable = {}

        for key, val in self.table.items():
            newtable[key] = val
        return newtable

    def add(self, key, value):
        self.table[key] = value
    

    def lookup(self, key):
        val = self.table.get(key, None)

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


    @staticmethod
    def openscope(p):
        return Scope(parent=p)

    