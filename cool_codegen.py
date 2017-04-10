from cool_ast import *
from cool_global import *
from collections import OrderedDict



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
        self.classObjTab = []

        self.inttable = {}
        self.stringtable = {}
        self.booltable = {}

        self.param_regs = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']
        self.predefinedClassName = ['Object', 'IO', 'Int', 'String', 'Bool']
        
        

    def genTag(self):
        # generate prime number for class tag
        self.tag += 1
        return self.tag

    def getSeqNum(self):
        self.seq += 1
        return self.seq


    def getPredeinedClasses(self):
        ObjectClass = Class(
            'Object',
            [
                FeatureMethodDecl('abort', [], 'Object', None),
                FeatureMethodDecl('type_name', [], 'String', None),
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


    def genGlobalData(self):

        ret = ""
        

        # generate prototype objects
        all_classes = self.getPredeinedClasses() + self.program.classes

        for c in all_classes:
            self.attrtable[c.className] = {}
            prototype = []
            
            prototype.append(self.genTag())         # tag

            attributes = [f for f in c.features if isinstance(f, FeatureAttribute)]
            prototype.append(len(attributes) + 1)   # size

            dispatchTab_lab = c.className + UNDERSCORE + DISPATCH_TABLE
            prototype.append(dispatchTab_lab)


            methodDecls = [f for f in c.features if isinstance(f, FeatureMethodDecl)]
            self.dispatchTable[c.className] = [c.className + UNDERSCORE + m.methodName for m in methodDecls] 


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
                        prototype.append("") # string
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

        # generate prototype object
        for className, values in self.prototypes.items():
            value_str =  NEWLINE.join([TAB + WORD + TAB + str(v) for v in values])
            ret += NEWLINE + className + UNDERSCORE + PROTOTYPE_SUFFIX + COLON + NEWLINE + value_str + NEWLINE

        # generate dispatch table
        for className, methods in self.dispatchTable.items():
            value_str = NEWLINE.join([TAB + WORD + TAB + str(m) for m in methods])
            ret += NEWLINE + className + UNDERSCORE + DISPATCH_TABLE + COLON + NEWLINE + value_str + NEWLINE

        # generate classObj table 
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



    def code_gen(self):
        ret = ".data" + NEWLINE
        ret += self.genGlobalData()


        ret += ".text" + NEWLINE
        ret += self.code_genProgram()

        return ret


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
            ret += TAB + "call {}".format(c.inheritType + UNDERSCORE + INIT) + NEWLINE

        for k, v in offset_info.items():
            ty = v['type']
            offset = v['offset']

            if ty == 'String':
                ret += TAB + "movq \'\', {}(%rbp)".format(offset) + NEWLINE
            elif ty == 'Bool' or ty == 'Int':
                ret += TAB + "movq 0, {}(%rbp)".format(offset) + NEWLINE
            else:
                ret += TAB + "movq 0, {}(%rbp)".format(offset) + NEWLINE

        


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

        if num_params > 0:
            ret += TAB + "subq %rsp, {}".format(str(self.wordsize * num_params)) + NEWLINE
            for i in range(num_params):
                if i < 6:
                    ret += TAB + "movq {}, -{}(%rbp)".format(str(self.param_regs[i]), str(i)) + NEWLINE
                else:
                    ret += TAB + "movq {}(%rbp), %rax".format(str(i + self.wordsize)) + NEWLINE
                    ret += TAB + "movq %rax, -{}(%rbp)".format(str(i)) + NEWLINE

                params_offset[method.formalParams[i].id] = -i

        
        ret += self.code_genExpr(c, params_offset, method.bodyExpr)
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
        string_lab = "string_const" + str(self.getSeqNum())
        self.stringtable[stringExpr.sval] = string_lab
        return TAB + "leaq {}(%rip), %rax".format(string_lab) + NEWLINE


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


            ret += TAB + "call {}_{}".format(c.className, methodName) + NEWLINE

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

            ret += TAB + "movq -4(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE
            ret += TAB + "movq %rax, {}({})",format(str(attr_offset), OBJ_ADDR_REG) + NEWLINE

        
        return ret


    def gen_selfObjAddress(self):

        return TAB + "movq -4(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE

    def genMethodEntry(self):
        return TAB + "pushq %rbp" + NEWLINE + TAB + "movq %rsp, %rbp" + NEWLINE

    def genMethodExit(self):
        return TAB + "movq %rbp, %rsp" + NEWLINE + TAB + "popq %rbp" + NEWLINE

if __name__ == "__main__":
    
    import sys
    import os
    import glob
    from parser import make_parser

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'

    parser = make_parser()

    with open("Tests/hello_world.cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    ret = parse_result.typecheck()
    cgen = CGen(parse_result)
    code = cgen.code_gen()

    print(code)
    print(cgen.attrtable)
    print(cgen.dispatchTable)
    

        
        
        


        


        