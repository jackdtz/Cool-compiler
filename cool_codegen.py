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
        self.attrtable = {}
        self.wordsize = 8

        self.prototypes = OrderedDict()
        self.dispatchTable = {}
        self.methodList = []

        self.param_regs = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']
        self.predefinedClassName = ['Object', 'IO', 'Int', 'String', 'Bool']
        self.rt_defined_methods = ['IO_in_int', 'IO_in_string']
        
        self.inttable = {}
        self.stringtable = {}
        self.booltable = {}
        self.tagtable = {}


        self.initialize()

    def initialize(self):
        seq = self.getSeqNum()
        self.inttable['0'] = "int_const" + str(seq)
        self.stringtable[''] = "string_const" + str(seq)


    def genTag(self):
        # generate prime number for class tag
        self.tag += 1
        return self.tag

    def getSeqNum(self):
        self.seq += 1
        return self.seq

    def genGloDirectives(self):

        ret = "\n"
        for name in self.methodList:
            ret += TAB + GLOBAL + TAB + name + NEWLINE

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
            ret += TAB + "callq {}".format(c.inheritType + UNDERSCORE + INIT) + NEWLINE

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
            ret += TAB + "subq $16, %rsp" + NEWLINE

        ret += TAB + "movq %rdi, 0(%rbp)" + NEWLINE

        if num_params > 0:
            # size_for_params = align(self.wordsize * num_params, ALIGNMENT_SIZE)
            # ret += TAB + "subq %rsp, {}".format(str(self.wordsize * (num_params)) + NEWLINE
            for i in range(1, num_params):
                if i < 6:
                    ret += TAB + "movq {}, -{}(%rbp)".format(str(self.param_regs[i]), str(i * self.wordsize)) + NEWLINE
                else:
                    ret += TAB + "movq {}(%rbp), %rax".format(str(i + self.wordsize)) + NEWLINE
                    ret += TAB + "movq %rax, -{}(%rbp)".format(str(i)) + NEWLINE

                params_offset[method.formalParams[i].id] = -i

        
        ret += self.code_genExpr(c, params_offset, method.bodyExpr)


        # restore stack
        if stack_size > 0:
            ret += TAB + "addq ${}, %rsp".format(str(stack_size * self.wordsize)) + NEWLINE
        else:
            ret += TAB + "addq $16, %rsp" + NEWLINE


        ret += self.genMethodExit()

        return label + COLON + NEWLINE + ret + NEWLINE


    
    def code_genExpr(self, c, params_offset, expr):
        if isinstance(expr, AssignmentExpr):
            return self.code_genAssignment(c, params_offset, expr)
        elif isinstance(expr, Dispatch):
            return self.code_genDispatch(c, params_offset, expr)
        elif isinstance(expr, String):
            return self.code_genString(c, params_offset, expr)


        
    def code_genString(self, c, params_offset, stringExpr):

        if stringExpr.sval in self.stringtable:
            string_lab = self.stringtable[stringExpr.sval]
        else:
            seq = self.getSeqNum()
            string_lab = "string_const" + str(seq)
            int_lab = "int_const" + str(seq)
            self.stringtable[stringExpr.sval] = string_lab
            self.inttable[str(len(stringExpr.sval))] = int_lab 

        # the actual string is located at offset 32, the fifth field
        ret = TAB + "leaq {}(%rip), %rax".format(string_lab) + NEWLINE
        ret += TAB + "addq ${}, %rax".format(STRCONST_STROFFSET) + NEWLINE

        return ret


    def code_genDispatch(self, c: 'Class', params_offset, dispatchExpr):
        ret = ""

        if isinstance(dispatchExpr.objExpr, Self):
            ret += self.gen_selfObjAddress()   # obj address is in rdi

            methodName = dispatchExpr.methodName

            arg_len = len(dispatchExpr.arguments)
            
            stack_count = 0
            for i, arg in reversed(list(enumerate(dispatchExpr.arguments))):
                ret += self.code_genExpr(c, params_offset, arg)
                if i < 5:   
                    # first reg is saved for SELF object
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

            ret += TAB + "callq* {}".format(DISP_FUNC_REG) + NEWLINE


            # ret += TAB + "callq {}_{}".format(c.className, methodName) + NEWLINE

            while stack_count > 0:
                ret += TAB + "popq %rax" + NEWLINE

            
            return ret

    def code_genAssignment(self, c: 'Class', params_offset, assignExpr):

        ret = ""

        lhs = assignExpr.id
        ret += code_genExpr(self, c.className, params_offset, assignExpr.expr)

        # formal params
        if lhs in params_offset:
            ret += TAB + "movq %rax, {}(%rbp)".format(params_offset[lhs]) + NEWLINE
            return ret

        if lhs in self.attrtable[c.className]:
            attr_offset = self.attrtable[c.className][lhs]

            ret += TAB + "movq -8(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE
            ret += TAB + "movq %rax, {}({})",format(str(attr_offset), OBJ_ADDR_REG) + NEWLINE

        
        return ret


    def gen_selfObjAddress(self):

        return TAB + "movq 0(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE

    def genMethodEntry(self):
        return TAB + "pushq %rbp" + NEWLINE + TAB + "movq %rsp, %rbp" + NEWLINE

    def genMethodExit(self):
        return TAB + "leave" + NEWLINE + TAB + "ret" + NEWLINE

if __name__ == "__main__":
    
    import sys
    import os
    import glob
    from parser import make_parser

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'

    parser = make_parser()

    file_name = "hello_world"


    with open("Tests/" + file_name + ".cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    ret = parse_result.typecheck()
    cgen = CGen(parse_result)
    code = cgen.code_gen()


    # with open("x86/" + filena )

    print(code)
    # print(cgen.attrtable)
    # print(cgen.dispatchTable)
    