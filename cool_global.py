
from cool_types import ObjectType, TopLevelClass, SelfType
from cool_types import StringType, BooleanType, IntegerType
from scope import *
from cool_values import *

objectType = ObjectType()
stringType = StringType(parent=objectType)
integerType = IntegerType(parent=objectType)
booleanType = BooleanType(parent=objectType)
selfType = SelfType()

topLevelClass = TopLevelClass("topLevel")

void = Void()

typecheckError = False




# Code Generation

SPACE = " "
TAB = SPACE * 4
NEWLINE = "\n"
UNDERSCORE = "_"
COLON = ":"
WORD = ".word"
GLOBAL = ".globl"
PROTOTYPE_SUFFIX = "protoObj"
DISPATCH_TABLE = "dispatch_table"
