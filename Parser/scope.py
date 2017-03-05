from collections import OrderedDict

class Scope(object):

    def __init__(self, parent=None):
        self.parent = parent

        # table is of type <string, map<string, object>>
        self.table = OrderedDict()

    