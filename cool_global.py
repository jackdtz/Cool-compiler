
from cool_types import ObjectType, TopLevelClass, SelfType
from cool_types import StringType, BooleanType, IntegerType
from scope import *

objectType = ObjectType()
stringType = StringType(parent=objectType)
integerType = IntegerType(parent=objectType)
booleanType = BooleanType(parent=objectType)
selfType = SelfType()

topLevelClass = TopLevelClass("topLevel")
