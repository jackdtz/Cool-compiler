
from .cool_types import ObjectType, TopLevelClass, SelfType
from .cool_types import StringType, BooleanType, IntegerType
from .scope import *
from .cool_values import *

objectType = ObjectType()
stringType = StringType(parent=objectType)
integerType = IntegerType(parent=objectType)
booleanType = BooleanType(parent=objectType)
selfType = SelfType()

topLevelClass = TopLevelClass("topLevel")

void = Void()


# Code Generation

SPACE = " "
TAB = SPACE * 4
DOT = "."
NEWLINE = "\n"
UNDERSCORE = "_"
COLON = ":"
WORD = ".quad"
ASCIZ = ".asciz"
ALIGN = ".align"
GLOBAL = ".globl"
PROTOTYPE_SUFFIX = "protoObj"
DISPATCH_TABLE = "dispatch_table"
INIT = "init"
OBJTABLE = "class_objTab"
OBJ_ADDR_REG = "%rdi"



TAG_OFFSET = '0'
SIZE_OFFSET = '8'
DISP_OFFSET = '16'
ATTR_OFFSET = '24'

DISP_FUNC_REG = "%r10"


STRCONST_STROFFSET = "32"
STRCONST_INTOFFSET = "24"
INTCONST_VALOFFSET = "24"

ALIGNMENT_SIZE = 16

STACK_SELF_OFFST = -40