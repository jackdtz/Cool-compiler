from typing import List

class Type(object):
    """
    The base class for all type, all other type class inherits
    this class
    """
    def __init__(self, parent: 'Type'=None):
        self.parent = parent

    def isSubclassOf(self, c: 'Type'):
        while self != None:
            if self == c:
                return True
            self = self.parent
        return False

    def lengthToRoot(self):
        """
        check the height of the type in the current type hierarchy 
        """
        count = 0
        s = self
        while s.parent != None:
            s = s.parent
            count += 1
        return count

    def mutualParentOfTwo(self, ty2):
        ty1 = self

        if not ty1 or not ty2:
            return None

        if ty1 == ty2:
            return ty1

        l1 = ty1.lengthToRoot()
        l2 = ty2.lengthToRoot()

        if l1 > l2:
            count = l1 - l2
            while count:
                ty1 = ty1.parent
                count -= 1
        elif l2 > l1:
            count = l2 - l1
            while count:
                ty2 = ty2.parent
                count -= 1

        while ty1 != ty2:
            ty1 = ty1.parent
            ty2 = ty2.parent

        if ty1 == ty2:
            return ty1

        return None

    @staticmethod        
    def mutualParentOfAll(tys: List['Type']):
        """
        takes in a list of types and return their mutual parent,
        return None if does not exist.
        """
        t = tys[0]
        for i in range(len(tys) - 1):
            t = t.mutualParentOfTwo(tys[i + 1])

        return t


class ObjectType(Type):
    pass


class FuncType(Type):
    def __init__(self, param_tys, ret_ty):
        super().__init__()
        self.param_tys = param_tys
        self.ret_ty = ret_ty


class PrimFuncType(Type):
    pass


class IntegerType(Type):
    pass


class StringType(Type):
    pass


class BooleanType(Type):
    pass


class SelfType(Type):
    pass


class ClassType(Type):
    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.name = name



class TopLevelClass(ClassType):
    pass



if __name__ == "__main__":
    classA = ClassType("a")
    classB = ClassType("b", parent=classA)

    print(classB.isSubclassOf(classA))