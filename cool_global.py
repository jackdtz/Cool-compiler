
from cool_types import ObjectType, TopLevelClass, SelfType
from cool_types import StringType, BooleanType, IntegerType, VoidType
from scope import *

objectType = ObjectType()
stringType = StringType(parent=objectType)
integerType = IntegerType(parent=objectType)
booleanType = BooleanType(parent=objectType)
selfType = SelfType()
voidType = VoidType()

topLevelClass = TopLevelClass("topLevel")
