from cool_ast import *
from cool_global import *
from collections import OrderedDict
from operator import itemgetter
from utilities import *

# %rax accumulator
# %rdi self object address

class CGen(object):

    def __init__(self, program: 'Program'):
        self.program = program

        self.tag = -1
        self.seq = -1
        self.condSeq = -1

        self.attrtable = {}
        self.wordsize = 8

        self.prototypes = OrderedDict()
        self.dispatchTable = {}
        self.methodList = []

        self.param_regs = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']
        self.caller_save = ['%rdx', '%rcx', '%rsi', '%rdi', '%r8', '%r9', '%r10']
        self.callee_save = ['%rbx', '%r12', '%r13', '%r14']


        self.predefinedClassName = ['Object', 'IO', 'Int', 'String', 'Bool']
        self.rt_defined_methods = ['IO_in_int', 'IO_in_string']
        
        self.inttable = {}
        self.stringtable = {}
        self.booltable = {}
        self.tagtable = {}

        self.initialize()

    def initialize(self):
        seq = self.genSeqNum()
        self.inttable['0'] = "int_const" + str(seq)
        self.stringtable[''] = "string_const" + str(seq)


    def genTag(self):
        # generate prime number for class tag
        self.tag += 1
        return self.tag

    def genSeqNum(self):
        self.seq += 1
        return self.seq

    def genCondSeq(self):
        self.condSeq += 1
        return self.condSeq


    def genGloDirectives(self):

        ret = "\n"
        ret += TAB + ".globl Main_init" + NEWLINE
        ret += TAB + ".globl Main_protoObj" + NEWLINE
        ret += TAB + ".globl Main_main" + NEWLINE
        ret += NEWLINE

        return ret

    def getPredeinedClasses(self):
        ObjectClass = Class(
            'Object',
            [
                FeatureMethodDecl('abort', [], 'Object', None),
                # FeatureMethodDecl('type_name', [], 'String', None),
                FeatureMethodDecl('copy', [], 'SELF_TYPE', None)
            ]
        )

        IOClass = Class(
            'IO',
            [
                FeatureMethodDecl('out_string', [FormalParam('x', 'String')], 'SELF_TYPE', None),
                FeatureMethodDecl('out_int', [FormalParam('x', 'Int')], 'SELF_TYPE', None),
                FeatureMethodDecl('in_string', [], 'String', None),
                FeatureMethodDecl('in_int', [], 'Int', None)
            ],
            'Object'
        )

        IntClass = Class('Int', [FeatureAttribute('value', 'Int', Integer(0))], 'Object')

        BoolClass = Class('Bool', [FeatureAttribute('value', 'Bool', Boolean(False))], 'Object')

        StringClass = Class(
            'String',
            [
                FeatureMethodDecl('length', [], 'Int', None),
                FeatureMethodDecl('concat', [FormalParam('s', 'String')], 'String', None),
                FeatureMethodDecl('substr', [FormalParam('i', 'Int'), FormalParam('l', 'Int')], 'String', None),
                FeatureAttribute('size', 'Int', Integer(0)),
                FeatureAttribute('value', 'String', String(""))
            ],
            'Object'
        )

        return [ObjectClass, IOClass, StringClass, IntClass, BoolClass]

    def collectGlobalData(self):

        # generate prototype objects
        all_classes = self.getPredeinedClasses() + self.program.classes

        for c in all_classes:
            self.attrtable[c.className] = {}
            prototype = []
            
            tag = self.genTag()
            self.tagtable[c.className] = tag
            prototype.append(tag)         # tag

            attributes = [f for f in c.features if isinstance(f, FeatureAttribute)]
            prototype.append(len(attributes) + 3)   # size

            dispatchTab_lab = c.className + UNDERSCORE + DISPATCH_TABLE
            prototype.append(dispatchTab_lab)


            methodDecls = [f for f in c.features if isinstance(f, FeatureMethodDecl)]
            self.dispatchTable[c.className] = [(c.className, m.methodName) for m in methodDecls] 

            # initialize attribute in the prototype object
            for i, attr in enumerate(attributes):
                if attr.decType == 'Int':
                    if not attr.init:
                        prototype.append(0)
                    else:
                        prototype.append(attr.init.ival)
                elif attr.decType == 'Bool':
                    if not attr.init:
                        prototype.append(0)
                    else:
                        prototype.append(1 if attr.init.bval else 0)
                elif attr.decType == 'String':
                    if not attr.init:
                        empty_string_label = self.stringtable['']
                        prototype.append(empty_string_label) # string
                    else:
                        prototype.append("\"" + attr.init.sval + "\"")
                
                self.attrtable[c.className][attr.id] = {}
                self.attrtable[c.className][attr.id]['offset'] = (i + 3) * self.wordsize
                self.attrtable[c.className][attr.id]['type'] = attr.decType
                
            self.prototypes[c.className] = prototype

        for c in all_classes:
            if c.inheritType:
                parentProtObj = self.prototypes[c.inheritType]
                parentAttrs = parentProtObj[3:]
                parentMethods = self.dispatchTable[c.inheritType]

                protoObj = self.prototypes[c.className]
                protoObjAttrs = protoObj[3:]
                self.prototypes[c.className] = protoObj[0:3] + parentAttrs + protoObjAttrs
                protoMethods = self.dispatchTable[c.className]
                self.dispatchTable[c.className] = parentMethods + protoMethods

    def code_genProtoTable(self):
        ret = ""

        # generate prototype object
        for className, values in self.prototypes.items():
            value_str =  NEWLINE.join([TAB + WORD + TAB + str(v) for v in values])
            ret += NEWLINE + className + UNDERSCORE + PROTOTYPE_SUFFIX + COLON + NEWLINE + value_str + NEWLINE

        return ret

    def translate_dispatchTable(self):
        # transfer dispatch table so that for each class, its methods map to an associated offset in the list
        for className, methodList in self.dispatchTable.items():
            newvalue = {}
            for index, method in enumerate(methodList):
                definedClassName = method[0]
                methodName = method[1]

                if methodName in newvalue:
                    newvalue[methodName]['definedClassName'] = definedClassName
                else:
                    newvalue[methodName] = {}
                    newvalue[methodName]['offset'] = index * self.wordsize
                    newvalue[methodName]['definedClassName'] = definedClassName

            self.dispatchTable[className] = newvalue

    def code_genDispatchTable(self):
        # generate dispatch table
        ret = ""
        self.translate_dispatchTable()
        for className, methodInfos in self.dispatchTable.items():

            sorted_methodInfos = sorted(methodInfos.items(), key=lambda value: value[1]['offset'])

            disp_value = []
            for (methodName, methodInfo) in sorted_methodInfos:
                disp_method_name = str(methodInfo['definedClassName']) + UNDERSCORE + str(methodName)
                if disp_method_name in self.rt_defined_methods:
                    disp_method_name = UNDERSCORE + disp_method_name

                
                disp_value.append(TAB + WORD + TAB + disp_method_name)
                self.methodList.append(disp_method_name)

            value_str = NEWLINE.join(disp_value)
            ret += NEWLINE + className + UNDERSCORE + DISPATCH_TABLE + COLON + NEWLINE + value_str + NEWLINE

        return ret

    def code_genClassObjTable(self):
        # generate classObj table 
        ret = "" 

        all_classnames = [c for c in self.prototypes.keys()]
        classObjs = []
        for className in all_classnames:
            protoLabel = className + UNDERSCORE + PROTOTYPE_SUFFIX
            initLabel = className + UNDERSCORE + INIT
            classObjs.append(protoLabel)
            classObjs.append(initLabel)
        classObjs_str = NEWLINE.join([TAB + WORD + TAB + str(name) for name in classObjs])

        ret += NEWLINE + OBJTABLE  + COLON + NEWLINE + classObjs_str + NEWLINE

        return ret

    def code_genIntConsts(self):
        int_consts = []

        int_tag = str(self.tagtable['Int'])
        size = '4'
        dispathTable = "Int_dispatch_table"

        for int_str, label in self.inttable.items():
            const = [
                TAB + WORD + TAB + int_tag + NEWLINE,
                TAB + WORD + TAB + size + NEWLINE,
                TAB + WORD + TAB + dispathTable + NEWLINE,
                TAB + WORD + TAB + int_str + NEWLINE 
            ]

            int_consts.append(label + COLON + NEWLINE + "".join(const))

        return NEWLINE.join(int_consts)

    def codeg_genStringConsts(self):

        string_consts = []
        string_tag = str(self.tagtable['String'])
        size = '6'
        dispathTable = "String_dispatch_table"

        for string, label in self.stringtable.items():
            len_const = self.inttable[str(len(string))]

            string = '\"\"' if string == '' else string

            const = [
                TAB + WORD + TAB + string_tag + NEWLINE,
                TAB + WORD + TAB + size + NEWLINE,
                TAB + WORD + TAB + dispathTable + NEWLINE,
                TAB + WORD + TAB + len_const + NEWLINE,
                TAB + ASCIZ + TAB + string + NEWLINE,
                TAB + ALIGN + TAB + str(self.wordsize) + NEWLINE
            ]

            string_consts.append(label + COLON + NEWLINE + "".join(const))

        return NEWLINE.join(string_consts)


#######################################################################################################################

    def code_gen(self):
        data_header = ".data" + NEWLINE

        self.collectGlobalData()
        data = self.code_genClassObjTable()
        data += self.code_genProtoTable()
        data += self.code_genDispatchTable()

        globl_directives = self.genGloDirectives()

        text_header = ".text" + NEWLINE
        text = self.code_genProgram()

        data += self.code_genIntConsts() + NEWLINE
        data += self.codeg_genStringConsts() + NEWLINE

        return data_header + globl_directives + data +  NEWLINE + text_header + text + NEWLINE


    def code_genProgram(self):

        ret = ""
        for c in self.getPredeinedClasses() + self.program.classes:
            ret += NEWLINE + self.code_genClass(c)

        return ret


    def code_genClass(self, c):

        ret = ""
        hasSeenInit = False

        for feature in c.features:
            if not isinstance(feature, FeatureMethodDecl):
                continue
            
            ret += NEWLINE + self.code_genMethod(c, feature)
            if c.className == "init":
                hasSeenInit = True

        if not hasSeenInit:
            ret += self.code_genDefaultInit(c)

        return ret

    def code_genDefaultInit(self, c: 'Class'):
        ret = self.genMethodEntry()

        offset_info = self.attrtable[c.className]

        if c.inheritType:
            ret += TAB + "movq %rdi, %rdi" + NEWLINE
            # ret += TAB + "callq {}".format(c.inheritType + UNDERSCORE + INIT) + NEWLINE
            ret += self.genFuncCall(c.inheritType + UNDERSCORE + INIT)

        for k, v in offset_info.items():
            ty = v['type']
            offset = v['offset']

            if ty == 'String':
                empty_string_label = self.stringtable['']
                ret += TAB + "leaq {}(%rip), %rax".format(empty_string_label) + NEWLINE
                ret += TAB + "movq %rax, {}(%rbp)".format(offset) + NEWLINE
            elif ty == 'Bool' or ty == 'Int':
                ret += TAB + "movq $0, {}(%rbp)".format(offset) + NEWLINE
            else:
                ret += TAB + "movq $0, {}(%rbp)".format(offset) + NEWLINE

        ret += self.genMethodExit()

        return c.className + UNDERSCORE + INIT + COLON + NEWLINE + ret + NEWLINE

    def code_genMethod(self, c: 'Class', method):
        if c.className in self.predefinedClassName:
            return ""

        params_offset = {}
        ret = ""
        
        if method.methodName == c.className:
            label = c.className + UNDERSCORE + INIT
        else:
            label = c.className + UNDERSCORE + method.methodName

        ret += self.genMethodEntry()

        num_params = len(method.formalParams)

        stack_size = align(max(0, num_params + 1 - 6) * self.wordsize, ALIGNMENT_SIZE)

        if stack_size > 0:
            ret += TAB + "subq ${}, %rsp".format(str(stack_size * self.wordsize)) + NEWLINE
        else:
            ret += TAB + "subq $8, %rsp" + NEWLINE

        ret += TAB + "movq %rdi, -40(%rbp)" + NEWLINE

        if num_params > 0:
            for i in range(1, num_params):
                if i < 6:
                    ret += TAB + "movq {}, -{}(%rbp)".format(str(self.param_regs[i]), str(i * self.wordsize)) + NEWLINE
                else:
                    ret += TAB + "movq {}(%rbp), %rax".format(str(i + self.wordsize)) + NEWLINE
                    ret += TAB + "movq %rax, -{}(%rbp)".format(str(i)) + NEWLINE

                params_offset[method.formalParams[i].id] = -i

        ret += self.code_genExpr(c, method, params_offset, method.bodyExpr)

        # restore stack
        if stack_size > 0:
            ret += TAB + "addq ${}, %rsp".format(str(stack_size * self.wordsize)) + NEWLINE
        else:
            ret += TAB + "addq $8, %rsp" + NEWLINE

        ret += self.genMethodExit()

        return label + COLON + NEWLINE + ret + NEWLINE

    def code_genExpr(self, c, method, params_offset, expr):
        if isinstance(expr, AssignmentExpr):
            return self.code_genAssignment(c, method, params_offset, expr)
        elif isinstance(expr, Dispatch):
            return self.code_genDispatch(c, method, params_offset, expr)
        elif isinstance(expr, String):
            return self.code_genString(c, method, params_offset, expr)
        elif isinstance(expr, Integer):
            return self.code_genInteger(c, method, params_offset, expr)
        elif isinstance(expr, If):
            return self.code_genIf(c, method, params_offset, expr)
        elif isinstance(expr, Boolean):
            return self.code_genBoolean(c, method, params_offset, expr)
        elif isinstance(expr, While):
            return self.code_genWhile(c, method, params_offset, expr)
        elif isinstance(expr, BinaryOp):
            return self.code_genBinary(c, method, params_offset, expr)
        elif isinstance(expr, Not):
            return self.code_genNot(c, method, params_offset, expr)
        elif isinstance(expr, Self):
            return self.code_genSelf(c, method, params_offset, expr)

    def code_genSelf(self, c, method, params_offset, selfExpr):
        return TAB + "movq -40(%rbp), %rax" + NEWLINE
    
    def code_genId(self, c, method, params_offset, idExpr):
       pass 

        
        
    def code_genNot(self, c, method, params_offset, expr):
        if isinstance(expr, GreaterThan):
            return code_genExpr(self, c, method, params_offset, LessEq(expr.e1, expr.e2))
        elif isinstance(expr, GreaterEq):
            return code_genExpr(self, c, method, params_offset, LessThan(expr.e1, expr.e2))
        elif isinstance(expr, Eq):
            return code_genExpr(self, c, method, params_offset, NotEq(expr.e1, expr.e2))
        elif isinstance(expr, NotEq):
            return code_genExpr(self, c, method, params_offset, Eq(expr.e1, expr.e2))
        elif isinstance(expr, LessThan):
            return code_genExpr(self, c, method, params_offset, GreaterEq(expr.e1, expr.e2))
        elif isinstance(expr, LessEq):
            return code_genExpr(self, c, method, params_offset, GreaterThan(expr.e1, expr.e2))
        else:
            exit("this should not happend - code genNode")
        

        


    def code_genBinayArith(self, c, method, params_offset, expr):
        if isinstance(expr, Plus):
            op = "addq"
        elif isinstance(expr, Minus):
            op = "subq"
        elif isinstance(expr, Multiply):
            op = "imul"

        elif isinstance(expr, Divide):
            print("ignore division for now")
            pass

        e1 = self.code_genExpr(c, method, params_offset, expr.e1)
        e2 = self.code_genExpr(c, method, params_offset, expr.e2)

        ret = e1 + NEWLINE
        ret += TAB + "push %rax" + NEWLINE
        ret += e2 + NEWLINE
        ret += TAB + "popq %rdi" + NEWLINE
        ret += TAB + "{} %rdi, %rax".format(op) + NEWLINE

        return ret

    def code_genBinary(self, c, method, params_offset, expr):

        if isinstance(expr, (Plus, Minus, Multiply, Divide)):
            return self.code_genBinayArith(c, method, params_offset, expr)
        
        # condition
        if isinstance(expr, GreaterThan):
            e = "g"
        elif isinstance(expr, GreaterEq):
            e = "ge"
        elif isinstance(expr, Eq):
            e = "e"
        elif isinstance(expr, LessThan):
            e = "l"
        elif isinstance(expr, LessEq):
            e = "le"
        elif isinstance(expr, NotEq):
            e = "ne"

        e1 = self.code_genExpr(c, method, params_offset, expr.e1)
        e2 = self.code_genExpr(c, method, params_offset, expr.e2)

        ret = e1
        ret += TAB + "pushq %rax" + NEWLINE
        ret += e2
        ret += TAB + "popq %rdi" + NEWLINE
        ret += TAB + "comp %rax, %rdi" + NEWLINE
        ret += TAB + "set{} %al" + NEWLINE
        ret += TAB + "movzbq %al, %rax" + NEWLINE

        return ret

    def code_genWhile(self, c, method, params_offset, whileExpr):

        seqNum = self.genSeqNum()

        begin_label = c.className + "." + method.methodName + ".loop_start." + str(seqNum)
        end_label = c.className + "." + method.methodName + ".loop_end." + str(seqNum)

        cnd = self.code_genExpr(c, method, params_offset, whileExpr.condition)
        body = self.code_genExpr(c, method, params_offset, whileExpr.bodyExpr)

        ret = begin_label + COLON + NEWLINE
        ret += cnd + NEWLINE
        ret += TAB + "cmpq $1, %rax" + NEWLINE
        ret += TAB + "jne {}".format(end_label) + NEWLINE
        ret += body + NEWLINE
        ret += TAB + "jmp {}".format(begin_label) + NEWLINE

        ret += end_label + COLON + NEWLINE

        return ret
        
    
    def code_genIf(self, c, method, params_offset, ifExpr):

        seqNum = self.genCondSeq()
        els_label = c.className + "."  + method.methodName + ".else." + str(seqNum)
        end_label = c.className + "."  + method.methodName + ".end." + str(seqNum)

        cnd = self.code_genExpr(c, method, params_offset, ifExpr.cnd)
        thn = self.code_genExpr(c, method, params_offset, ifExpr.thn)
        els = self.code_genExpr(c, method, params_offset, ifExpr.els)

        ret = TAB + "cmpq $1, %rax" + NEWLINE
        ret += TAB + "jne {}".format(els_label) + NEWLINE
        ret += thn + NEWLINE
        ret += TAB + "jmp {}".format(end_label) + NEWLINE
        ret += NEWLINE
        ret += els_label + COLON + NEWLINE
        ret += els + NEWLINE
        ret += end_label + COLON + NEWLINE

        return cnd + ret

    def code_genBoolean(self, c, method, params_offset, booleanExpr):
        if booleanExpr.bval:
            return TAB + "movq $1, %rax" + NEWLINE
        
        return TAB + "movq $0, %rax" + NEWLINE

    def code_genString(self, c, method, params_offset, stringExpr):

        if stringExpr.sval in self.stringtable:
            string_lab = self.stringtable[stringExpr.sval]
        else:
            seq = self.genSeqNum()
            string_lab = "string_const" + str(seq)
            int_lab = "int_const" + str(seq)
            self.stringtable[stringExpr.sval] = string_lab
            self.inttable[str(len(stringExpr.sval))] = int_lab 

        # the actual string is located at offset 32, the fifth field
        ret = TAB + "leaq {}(%rip), %rax".format(string_lab) + NEWLINE
        ret += TAB + "addq ${}, %rax".format(STRCONST_STROFFSET) + NEWLINE

        return ret

    def code_genInteger(self, c, method, params_offset, intExpr):
        if intExpr.ival in self.inttable:
            int_label = self.inttable[str(intExpr.ival)]
        else:
            seq = self.genSeqNum()
            int_label = "int_const" + str(seq)
            self.inttable[str(intExpr.ival)] = int_label

        ret = TAB + "leaq {}(%rip), %rax".format(int_label) + NEWLINE
        ret += TAB + "addq ${}, %rax".format(INTCONST_VALOFFSET) + NEWLINE

        return ret

    def code_genDispatch(self, c: 'Class', method, params_offset, dispatchExpr):
        ret = ""

        ret += self.code_genExpr(c, method, params_offset, dispatchExpr.objExpr)
        ret += TAB + "movq %rax, %rdi" + NEWLINE

        methodName = dispatchExpr.methodName
        arg_len = len(dispatchExpr.arguments)
        
        stack_count = 0
        for i, arg in reversed(list(enumerate(dispatchExpr.arguments))):
            ret += self.code_genExpr(c, method, params_offset, arg)
            if i < 5:   
                # first reg is saved for object (could be SELF or other type)
                ret += TAB + "movq %rax, {}".format(self.param_regs[i + 1]) + NEWLINE
            else:
                ret += TAB + "pushq %rax" + NEWLINE
                stack_count += 1

        # we will use r10 to store to vtable address
        ret += TAB + "movq {}(%rdi), {}".format(DISP_OFFSET, DISP_FUNC_REG) + NEWLINE

        # get the function offset from dispatch table
        offset = self.dispatchTable[c.className][methodName]['offset']
        
        # use offset to get the appropriate function
        ret += TAB + "movq {}({}), {}".format(str(offset), DISP_FUNC_REG, DISP_FUNC_REG) + NEWLINE

        ret += self.genFuncCall('*' + DISP_FUNC_REG)

        while stack_count > 0:
            ret += TAB + "popq %rax" + NEWLINE

        return ret

    def code_genAssignment(self, c: 'Class', method, params_offset, assignExpr):
        ret = ""

        lhs = assignExpr.id
        ret += self.code_genExpr(c, method, params_offset, assignExpr.expr)

        # formal params
        if lhs in params_offset:
            ret += TAB + "movq %rax, {}(%rbp)".format(params_offset[lhs]) + NEWLINE
            return ret

        if lhs in self.attrtable[c.className]:
            attr_offset = self.attrtable[c.className][lhs]

            ret += TAB + "movq -40(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE
            ret += TAB + "movq %rax, {}({})",format(str(attr_offset), OBJ_ADDR_REG) + NEWLINE

        return ret

    def gen_selfObjAddress(self):
        return TAB + "movq -40(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE

    def genMethodEntry(self):
        ret = TAB + "pushq %rbp" + NEWLINE + TAB + "movq %rsp, %rbp" + NEWLINE
        for reg in self.callee_save:
            ret += TAB + "pushq {}".format(reg) + NEWLINE
        return ret

    def genMethodExit(self):
        ret = ""
        for reg in list(reversed(self.callee_save)):
            ret += TAB + "popq {}".format(reg) + NEWLINE

        return ret + TAB + "leave" + NEWLINE + TAB + "ret" + NEWLINE

    def genFuncCall(self, name):
        ret = ""

        for reg in self.caller_save:
            ret += TAB + "pushq {}".format(reg) + NEWLINE

        ret += TAB + "callq {}".format(name) + NEWLINE

        for reg in list(reversed(self.caller_save)):
            ret += TAB + "popq {}".format(reg) + NEWLINE

        return ret

        

if __name__ == "__main__":
    
    import sys
    import os
    import glob
    from parser import make_parser

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'

    parser = make_parser()

    file_name = "while"


    with open("Tests/" + file_name + ".cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    ret = parse_result.typecheck()
    cgen = CGen(parse_result)
    code = cgen.code_gen()


    # with open("x86/" + filena )

    print(code)
    # print(cgen.attrtable)
    # print()
    # print(cgen.dispatchTable)
    # print()
    # print(cgen.prototypes)
    