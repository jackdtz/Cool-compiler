from .cool_ast import *
from .cool_global import *
from collections import OrderedDict
from operator import itemgetter
from .utilities import *

# %rax accumulator
# %rdi self object address

class CGen(object):

    def __init__(self, program: 'Program', type_scope: 'Scope'):
        self.program = program
        self.type_scope = type_scope

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
        self.rt_defined_methods = ['IO_in_int']
        
        self.inttable = {}
        self.stringtable = {}
        self.str_contenttable = {}
        self.booltable = {}
        self.tagtable = {}

        self.initialize()
        self.scope = CGen_scope()

    def initialize(self):
        seq = self.genSeqNum()
        self.inttable['0'] = "int_const" + str(seq)
        
        self.stringtable[''] = {}
        self.stringtable['']['label'] = "string_const" + str(seq)
        self.stringtable['']['content'] = "string_content" + str(seq)
        self.str_contenttable["string_content" + str(seq)] = ""


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
        ret += TAB + ".globl String_protoObj" + NEWLINE
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

        attr_start_index = 3

        # generate prototype objects
        all_classes = self.getPredeinedClasses() + self.program.classes

        for c in all_classes:
            self.attrtable[c.className] = {}
            prototype = []
            
            tag = self.genTag()
            self.tagtable[c.className] = tag
            prototype.append(tag)         # tag

            attributes = [f for f in c.features if isinstance(f, FeatureAttribute)]
            prototype.append(len(attributes) + attr_start_index)   # size

            dispatchTab_lab = c.className + UNDERSCORE + DISPATCH_TABLE
            prototype.append(dispatchTab_lab)


            methodDecls = [f for f in c.features if isinstance(f, FeatureMethodDecl)]
            self.dispatchTable[c.className] = [(c.className, m.methodName) for m in methodDecls] 

            # initialize attribute all to 0 in the prototype object
            for i, attr in enumerate(attributes):
                prototype.append(0)

                self.attrtable[c.className][attr.id] = {}
                self.attrtable[c.className][attr.id]['offset'] = (i + attr_start_index) * self.wordsize
                self.attrtable[c.className][attr.id]['type'] = attr.decType
                
            self.prototypes[c.className] = prototype

        for c in all_classes:
            if c.inheritType:
                parentProtObj = self.prototypes[c.inheritType]
                parentAttrs = parentProtObj[attr_start_index :]
                parentMethods = self.dispatchTable[c.inheritType]

                protoObj = self.prototypes[c.className]
                protoObjAttrs = protoObj[attr_start_index:]
                self.prototypes[c.className] = protoObj[0:attr_start_index] + parentAttrs + protoObjAttrs
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

        for string, info in self.stringtable.items():
            len_const = self.inttable[str(len(string))]
            label = info['label']
            content_label = info['content']

            string = '\"\"' if string == '' else string

            const = [
                TAB + WORD + TAB + string_tag + NEWLINE,
                TAB + WORD + TAB + size + NEWLINE,
                TAB + WORD + TAB + dispathTable + NEWLINE,
                TAB + WORD + TAB + len_const + NEWLINE,
                TAB + WORD + TAB + content_label + NEWLINE,
                TAB + ALIGN + TAB + str(self.wordsize) + NEWLINE
            ]

            string_consts.append(label + COLON + NEWLINE + "".join(const))

        return NEWLINE.join(string_consts)


    def code_genInitValue(self, ty):

        ret = ""

        if ty == "Int":
            zero_label = self.inttable['0']
            ret += TAB + "leaq {}(%rip), %rax".format(zero_label) + NEWLINE
            # ret += TAB + "movq {}(%rax), %rax".format(INTCONST_VALOFFSET) + NEWLINE
            # ret += TAB + "movq (%rax), %rax" + NEWLINE
        elif ty == "String":
            empty_label = self.stringtable['']['label']
            ret += TAB + "leaq {}(%rip), %rax".format(empty_label) + NEWLINE
            # ret += TAB + "movq {}(%rax), %rax".format(STRCONST_STROFFSET) + NEWLINE
        elif ty == "Bool":
            ret += TAB + "movq $0, %rax" + NEWLINE
        

        return ret


    def code_genConstantContent(self):

        ret = "" + NEWLINE + NEWLINE

        for content_label, value in self.str_contenttable.items():
            value = "\"\"" if value == "" else value
            ret +=  content_label + COLON + NEWLINE + \
                TAB + ASCIZ + TAB + value + NEWLINE + \
                TAB + ALIGN + TAB + "8" + NEWLINE

        # for content_label, value in self.int_contenttable.items():
        #     ret += content_label + COLON + TAB + WORD + TAB + value + NEWLINE 

        return ret + NEWLINE
        
            



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

        const_content = self.code_genConstantContent() + NEWLINE

        data += self.code_genIntConsts() + NEWLINE
        data += self.codeg_genStringConsts() + NEWLINE

        return data_header + globl_directives + const_content + data +  NEWLINE + text_header + text + NEWLINE


    def code_genProgram(self):

        ret = ""
        for c in self.getPredeinedClasses() + self.program.classes:
            ret += NEWLINE + self.code_genClass(c)

        return ret


    def code_genClass(self, c):

        ret = ""
        self.scope.enterScope()

        hasSeenInit = False
        hasAttrbutes = True if self.attrtable[c.className] else False

        for feature in c.features:
            if not isinstance(feature, FeatureMethodDecl):
                continue
            
            if feature.methodName == "init":
                hasSeenInit = True
                if hasAttrbutes:
                    feature = self.addAttrInitToFeature(c, feature)

            ret += NEWLINE + self.code_genMethod(c, feature)

        if not hasSeenInit and not hasAttrbutes:
            ret += self.gen_emptyInit(c)
        elif not hasSeenInit:
            defaultMethod = self.generateDefaulInit(c)
            ret += self.code_genMethod(c, defaultMethod)
        elif not hasAttrbutes:
            pass
            
    
        return ret

    def addAttrInitToFeature(self, c, method):
        attrs = self.getAttributesFromClass(c)

        new_body = Block([])

        for id, initInfo in attrs.items():
            ty = initInfo[0]
            init = initInfo[1]

            if ty == 'String':
                rvalue = init if init else String("")
            elif ty == "Int":
                rvalue = init if init else Integer(0)
            elif ty == "Bool":
                rvalue = init if init else Boolean(False)
            else:
                rvalue = init if init else Integer(-1)

            body.exprs.append(AssignmentExpr(id, rvalue))

        new_body.exprs.append(method.bodyExpr)
        method.bodyExpr = new_body

        return method

    def generateDefaulInit(self, c: 'class'):
        attrs = self.getAttributesFromClass(c)
        body = Block([])

        for id, initInfo in attrs.items():
            ty = initInfo[0]
            init = initInfo[1]

            if ty == 'String':
                rvalue = init if init else String("")
            elif ty == "Int":
                rvalue = init if init else Integer(0)
            elif ty == "Bool":
                rvalue = init if init else Boolean(False)
            else:
                rvalue = init if init else Integer(-1)

            body.exprs.append(AssignmentExpr(id, rvalue))

        return FeatureMethodDecl('init', [], 'Object', body)


    def gen_emptyInit(self, c: 'Class'):
        ret = self.genMethodEntry()

        if c.inheritType:
            ret += self.genFuncCall(c.inheritType + UNDERSCORE + INIT)

        ret += self.genMethodExit()

        return c.className + UNDERSCORE + INIT + COLON + NEWLINE + ret + NEWLINE

    def getAttributesFromClass(self, c):
        return dict([(f.id, (f.decType, f.init)) for f in c.features if isinstance(f, FeatureAttribute)])

    def code_genMethod(self, c: 'Class', method):
        if c.className in self.predefinedClassName and method.methodName != 'init':
            return ""

        # params_offset = {}
        self.scope.enterScope()
        ret = ""
        
        if method.methodName == c.className:
            label = c.className + UNDERSCORE + INIT
        else:
            label = c.className + UNDERSCORE + method.methodName

        ret += self.genMethodEntry()

        if method.methodName == "init" and c.inheritType:
            ret += self.genFuncCall("{}_init".format(c.inheritType))

        num_params = len(method.formalParams) + 1

        # this will be used to calculate the offset of local from base pointer
        num_locals = num_params

        stack_size = align(num_params * self.wordsize, ALIGNMENT_SIZE)

        ret += TAB + "subq ${}, %rsp".format(stack_size) + NEWLINE

        if num_params > 0:
            for i in range(num_params):
                if i < 6:
                    source_reg = self.param_regs[i]
                    target_offset = -(i + 5) * self.wordsize
                    ret += TAB + "movq {}, {}(%rbp)".format(source_reg, target_offset) + NEWLINE
                else:
                    target_offset = -(i + 5) * self.wordsize
                    ret += TAB + "movq {}(%rbp), %rax".format(i + self.wordsize) + NEWLINE
                    ret += TAB + "movq %rax, {}(%rbp)".format(target_offset) + NEWLINE

                # offset always starts 32 bytes from the base pointer 
                # since those 32 bytes are used for storing callee save regs content
                if i == 0 : # self
                    self.scope.addId('self', -(i + 5) * self.wordsize, c.className)
                else:
                    id = method.formalParams[i - 1].id
                    ty = method.formalParams[i - 1].decType
                    self.scope.addId(id, -(i + 5) * self.wordsize, ty)

        body_code, _ = self.code_genExpr(c, method, num_locals, method.bodyExpr)
        
        ret += body_code

        # restore stack
        ret += TAB + "addq ${}, %rsp".format(stack_size) + NEWLINE

        ret += self.genMethodExit()
        self.scope.existScope()

        return label + COLON + NEWLINE + ret + NEWLINE

    def code_genExpr(self, c, method, num_locals, expr, isLvalue=False):
        if isinstance(expr, AssignmentExpr):
            return self.code_genAssignment(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Dispatch):
            return self.code_genDispatch(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, String):
            return self.code_genString(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Integer):
            return self.code_genInteger(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, If):
            return self.code_genIf(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Boolean):
            return self.code_genBoolean(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, While):
            return self.code_genWhile(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, BinaryOp):
            return self.code_genBinary(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Not):
            return self.code_genNot(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Self):
            return self.code_genSelf(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Id):
            return self.code_genId(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Block):
            return self.code_genBlock(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Let):
            return self.code_genLet(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, ParenExpr):
            return self.code_genExpr(c, method, num_locals, expr.e, isLvalue)
        elif isinstance(expr, NewConstruct):
            return self.code_genNew(c, method, num_locals, expr, isLvalue)
        elif isinstance(expr, Neg):
            return self.code_genNeg(c, method, num_locals, expr, isLvalue)

    def code_genNeg(self, c, method, num_locals, expr, isLvalue):
        expr_code, expr_type = self.code_genExpr(c, method, num_locals, expr.expr, isLvalue)

        return expr_code + TAB + "negq %rax" + NEWLINE, expr_type

    def code_genNew(self, c, method, num_locals, newExpr, isLvalue):
        object_name = newExpr.objType

        ret = TAB + "leaq {}_protoObj(%rip), %rdi".format(object_name) + NEWLINE
        ret += self.genFuncCall("Object_copy") + NEWLINE
        ret += TAB + "movq %rax, %rdi" + NEWLINE
        ret += TAB + "pushq %rax" + NEWLINE
        ret += TAB + "subq $8, %rsp" + NEWLINE
        ret += self.genFuncCall("{}_init".format(object_name)) + NEWLINE
        ret += TAB + "addq $8, %rsp" + NEWLINE
        ret += TAB + "popq %rax" + NEWLINE

        return ret, object_name

    def code_genLet(self, c, method, num_locals, letExpr, isLvalue):

        self.scope.enterScope()
        decl_num = len(letExpr.declareVars)

        # save space on the stack for let varaibles
        stack_size = align(decl_num * self.wordsize, ALIGNMENT_SIZE)
        ret = TAB + "subq ${}, %rsp".format(stack_size) + NEWLINE

        for i, varDecl in enumerate(letExpr.declareVars):
            id = varDecl.id
            offset =  -(i + num_locals + 5) * self.wordsize
            self.scope.addId(id, offset, varDecl.decType)

            if varDecl.init:
                init, _ = self.code_genExpr(c, method, num_locals + decl_num, varDecl.init, True)
            else:
                init = self.code_genInitValue(varDecl.decType)
                
            ret += init
            ret += TAB + "movq %rax, {}(%rbp)".format(offset) + NEWLINE

        body, body_type = self.code_genExpr(c, method, num_locals + decl_num, letExpr.bodyExpr, isLvalue)

        ret += body
        self.scope.existScope()

        return ret, body_type     

    def code_genBlock(self, c, method, num_locals, block, isLvalue):

        codes = []
        for i in range(len(block.exprs) - 1):
            ret, _ = self.code_genExpr(c, method, num_locals, block.exprs[i], isLvalue)
            codes.append(ret)
        
        last_code, ty = self.code_genExpr(c, method, num_locals, block.exprs[-1], isLvalue)
        codes.append(last_code)

        return NEWLINE.join(codes), ty

    def code_genSelf(self, c, method, num_locals, selfExpr, isLvalue):
        return TAB + "movq {}(%rbp), %rax".format(STACK_SELF_OFFST) + NEWLINE, 'Self'
    
    def code_genId(self, c, method, num_locals, idExpr, isLvalue):

        ret = ""
        ty = None

        offset = self.scope.lookup_offset(idExpr.id)
        if offset:
            ty = self.scope.lookup_type(idExpr.id)
            ret += TAB + "movq {}(%rbp), %rax".format(offset) + NEWLINE

        # id is an instance variable
        if idExpr.id in self.attrtable[c.className]:
            object_addr_offset = self.scope.lookup_offset('self')
            object_attr_offset = self.attrtable[c.className][idExpr.id]['offset']
            object_attr_type = self.attrtable[c.className][idExpr.id]['type']
            ty = object_attr_type

            ret = TAB + "movq {}(%rbp), %rax".format(object_addr_offset) + NEWLINE
            ret += TAB + "movq {}(%rax), %rax".format(object_attr_offset) + NEWLINE

        if self.scope.lookup_type(idExpr.id) == 'Int' or self.attrtable[c.className][idExpr.id]['type'] == 'Int':
            if not isLvalue:
                ret += TAB + "movq {}(%rax), %rax".format(INTCONST_VALOFFSET) + NEWLINE

        return ret, ty

        exit("{} not in params_offset").format(idExpr.id)

    def code_genNot(self, c, method, num_locals, expr, isLvalue):
        if isinstance(expr, GreaterThan):
            return code_genExpr(self, c, method, num_locals, LessEq(expr.e1, expr.e2), isLvalue)
        elif isinstance(expr, GreaterEq):
            return code_genExpr(self, c, method, num_locals, LessThan(expr.e1, expr.e2), isLvalue)
        elif isinstance(expr, Eq):
            return code_genExpr(self, c, method, num_locals, NotEq(expr.e1, expr.e2), isLvalue)
        elif isinstance(expr, NotEq):
            return code_genExpr(self, c, method, num_locals, Eq(expr.e1, expr.e2), isLvalue)
        elif isinstance(expr, LessThan):
            return code_genExpr(self, c, method, num_locals, GreaterEq(expr.e1, expr.e2), isLvalue)
        elif isinstance(expr, LessEq):
            return code_genExpr(self, c, method, num_locals, GreaterThan(expr.e1, expr.e2), isLvalue)
        else:
            exit("this should not happend - code genNode")
        
    def code_genBinaryArith(self, c, method, num_locals, expr, isLvalue):
        if isinstance(expr, Plus):
            op = "addq"
        elif isinstance(expr, Minus):
            op = "subq"
        elif isinstance(expr, Multiply):
            op = "imulq"
        elif isinstance(expr, Divide):
            op = "idivq"

        e1, ty1 = self.code_genExpr(c, method, num_locals, expr.e1, False)
        e2, ty2 = self.code_genExpr(c, method, num_locals, expr.e2, False)



        ret = e1 + NEWLINE
        ret += TAB + "push %rax" + NEWLINE
        ret += e2 + NEWLINE
        ret += TAB + "movq %rax, %rdi" + NEWLINE        #e2 : rdi
        ret += TAB + "popq %rax" + NEWLINE              #e1 : rax
        if op == "idivq":
            ret += TAB + "xorq %rdx, %rdx" + NEWLINE
            ret += TAB + "idivq %rdi" + NEWLINE
        else:
            ret += TAB + "{} %rdi, %rax".format(op) + NEWLINE

        ret += TAB + "movq %rax, %rdi" + NEWLINE
        ret += TAB + "pushq %rdi" + NEWLINE
        ret += TAB + "subq $8, %rsp" + NEWLINE

        newcode, _ = self.code_genNew(c, method, num_locals, NewConstruct("Int"), isLvalue)
        ret += newcode + NEWLINE
        ret += TAB + "addq $8, %rsp" + NEWLINE
        ret += TAB + "popq %rdi" + NEWLINE
        ret += TAB + "movq %rdi, {}(%rax)".format(INTCONST_VALOFFSET) + NEWLINE

        return ret, 'Int'

    def code_genBinary(self, c, method, num_locals, expr, isLvalue):

        if isinstance(expr, (Plus, Minus, Multiply, Divide)):
            return self.code_genBinaryArith(c, method, num_locals, expr, isLvalue)
        
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

        e1, _ = self.code_genExpr(c, method, num_locals, expr.e1, False)
        e2, _ = self.code_genExpr(c, method, num_locals, expr.e2, False)

        

        ret = e1
        ret += TAB + "pushq %rax" + NEWLINE
        ret += e2
        ret += TAB + "popq %rdi" + NEWLINE
        ret += TAB + "cmpq %rax, %rdi" + NEWLINE
        ret += TAB + "set{} %al".format(e) + NEWLINE
        ret += TAB + "movzbq %al, %rax" + NEWLINE

        return ret, 'Bool'

    def code_genWhile(self, c, method, num_locals, whileExpr, isLvalue):

        seqNum = self.genSeqNum()

        begin_label = c.className + "." + method.methodName + ".loop_start." + str(seqNum)
        end_label = c.className + "." + method.methodName + ".loop_end." + str(seqNum)

        cnd, _ = self.code_genExpr(c, method, num_locals, whileExpr.condition, False)
        body, _ = self.code_genExpr(c, method, num_locals, whileExpr.bodyExpr, isLvalue)

        ret = begin_label + COLON + NEWLINE
        ret += cnd + NEWLINE
        ret += TAB + "cmpq $1, %rax" + NEWLINE
        ret += TAB + "jne {}".format(end_label) + NEWLINE
        ret += body + NEWLINE
        ret += TAB + "jmp {}".format(begin_label) + NEWLINE

        ret += end_label + COLON + NEWLINE

        return ret, 'Object'
        
    
    def code_genIf(self, c, method, num_locals, ifExpr, isLvalue):

        seqNum = self.genCondSeq()
        els_label = c.className + "."  + method.methodName + ".else." + str(seqNum)
        end_label = c.className + "."  + method.methodName + ".end." + str(seqNum)

        cnd, _ = self.code_genExpr(c, method, num_locals, ifExpr.cnd, isLvalue)
        thn, _ = self.code_genExpr(c, method, num_locals, ifExpr.thn, True)
        els, _ = self.code_genExpr(c, method, num_locals, ifExpr.els, True)

        ret = TAB + "cmpq $1, %rax" + NEWLINE
        ret += TAB + "jne {}".format(els_label) + NEWLINE
        ret += thn + NEWLINE
        ret += TAB + "jmp {}".format(end_label) + NEWLINE
        ret += NEWLINE
        ret += els_label + COLON + NEWLINE
        ret += els + NEWLINE
        ret += end_label + COLON + NEWLINE

        return cnd + ret, _

    def code_genBoolean(self, c, method, num_locals, booleanExpr, isLvalue):
        if booleanExpr.bval:
            return TAB + "movq $1, %rax" + NEWLINE, 'Bool'
        
        return TAB + "movq $0, %rax" + NEWLINE, 'Bool'

    def code_genString(self, c, method, num_locals, stringExpr, isLvalue):

        if stringExpr.sval in self.stringtable:
            string_lab = self.stringtable[stringExpr.sval]['label']
        else:
            seq = self.genSeqNum()
            string_lab = "string_const" + str(seq)
            string_content_lab = "string_content" + str(seq)
            self.stringtable[stringExpr.sval] = {}
            self.stringtable[stringExpr.sval]['content'] = string_content_lab
            self.stringtable[stringExpr.sval]['label'] = string_lab
            self.str_contenttable[string_content_lab] = stringExpr.sval

            if not str(len(stringExpr.sval)) in self.inttable:
                int_lab = "int_const" + str(seq)
                self.inttable[str(len(stringExpr.sval))] = int_lab



        
        ret = TAB + "leaq {}(%rip), %rax".format(string_lab) + NEWLINE

        if isLvalue:
            return ret, 'String'

        # # the actual string is located at offset 32, the fifth field
        ret += TAB + "movq {}(%rax), %rax".format(STRCONST_STROFFSET) + NEWLINE

        return ret, 'String'

    def code_genInteger(self, c, method, num_locals, intExpr, isLvalue):
        if str(intExpr.ival) in self.inttable:
            int_label = self.inttable[str(intExpr.ival)]
        else:
            seq = self.genSeqNum()
            int_label = "int_const" + str(seq)
            self.inttable[str(intExpr.ival)] = int_label

        # get constant object address, then get content at offset
        ret = TAB + "leaq {}(%rip), %rax".format(int_label) + NEWLINE

        if isLvalue:
            return ret, 'Int'

        ret += TAB + "movq {}(%rax), %rax".format(INTCONST_VALOFFSET) + NEWLINE

        return ret, 'Int'

    def code_genDispatch(self, c: 'Class', method, num_locals, dispatchExpr, isLvalue):
        ret = ""

        obj_code, obj_ty = self.code_genExpr(c, method, num_locals, dispatchExpr.objExpr, True)
        ret += obj_code
        ret += TAB + "push %rdi" + NEWLINE
        ret += TAB + "subq $8, %rsp" + NEWLINE
        ret += TAB + "movq %rax, %rdi" + NEWLINE

        methodName = dispatchExpr.methodName
        arg_len = len(dispatchExpr.arguments)

        # rdi might be used in code_gen for arguments, so we need to push it again
        ret += TAB + "push %rdi" + NEWLINE
        ret += TAB + "subq $8, %rsp" + NEWLINE
        
        stack_count = 0
        for i, arg in reversed(list(enumerate(dispatchExpr.arguments))):
            arg_code, _ = self.code_genExpr(c, method, num_locals, arg, True)

            # ret += self.caller_save_push()
            ret += arg_code
            # ret += self.caller_save_pop()

            if i < 5:   
                # first reg is saved for object (could be SELF or other type)
                ret += TAB + "movq %rax, {}".format(self.param_regs[i + 1]) + NEWLINE
            else:
                ret += TAB + "pushq %rax" + NEWLINE
                stack_count += 1
        

        ret += TAB + "addq $8, %rsp" + NEWLINE
        ret += TAB + "popq %rdi" + NEWLINE
        ret += TAB + "movq {}(%rdi), {}".format(DISP_OFFSET, DISP_FUNC_REG) + NEWLINE

        # get the function offset from dispatch table
        if obj_ty == 'Self': obj_ty = c.className
        offset = self.dispatchTable[obj_ty][methodName]['offset']
        
        # use offset to get the appropriate function
        ret += TAB + "movq {}({}), {}".format(str(offset), DISP_FUNC_REG, DISP_FUNC_REG) + NEWLINE
        ret += self.genFuncCall('*' + DISP_FUNC_REG)

        while stack_count > 0:
            ret += TAB + "popq %rax" + NEWLINE
            stack_count -= 1

        ret += TAB + "addq $8, %rsp" + NEWLINE
        ret += TAB + "popq %rdi" + NEWLINE

        ret_type = str(self.type_scope.lookup(c.className).lookupType(method.methodName).ret_ty)

        if not isLvalue and ret_type == 'Int':
            ret += TAB + "movq {}(%rax), %rax".format(INTCONST_VALOFFSET) + NEWLINE


        return ret, ret_type

    def code_genAssignment(self, c: 'Class', method, num_locals, assignExpr, isLvalue):
        ret = ""

        lhs = assignExpr.id
        rhs_code, rhs_ty = self.code_genExpr(c, method, num_locals, assignExpr.expr, True)

        ret += rhs_code

        # if it is in scope
        offset = self.scope.lookup_offset(lhs)
        if offset:
            ret += TAB + "movq %rax, {}(%rbp)".format(offset) + NEWLINE
            return ret, rhs_ty

        if lhs in self.attrtable[c.className]:
            attr_offset = self.attrtable[c.className][lhs]['offset']

            # -40 is the offset to access self obj
            ret += TAB + "movq {}(%rbp), {}".format(STACK_SELF_OFFST, OBJ_ADDR_REG) + NEWLINE
            ret += TAB + "movq %rax, {}({})".format(attr_offset, OBJ_ADDR_REG) + NEWLINE

        return ret, rhs_ty

    def gen_selfObjAddress(self):
        return TAB + "movq {}(%rbp), {}".format(OBJ_ADDR_REG) + NEWLINE

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

        ret += self.caller_save_push()
        
        ret += TAB + "callq {}".format(name) + NEWLINE

        ret += self.caller_save_pop()

        return ret

    def caller_save_push(self):
        ret = ""

        for reg in self.caller_save:
            ret += TAB + "pushq {}".format(reg) + NEWLINE

        
        # there are 7 caller save regs, so we need 8 more bytes to 
        # make sure that the stack is 16 bytes aligned
        ret += TAB + "subq $8, %rsp" + NEWLINE

        return ret

    def caller_save_pop(self):

        ret = ""
        ret += TAB + "addq $8, %rsp" + NEWLINE


        for reg in list(reversed(self.caller_save)):
            ret += TAB + "popq {}".format(reg) + NEWLINE

        return ret



        

if __name__ == "__main__":
    
    import sys
    import os
    import glob
    from parser import make_parser
    from os.path import basename
    import subprocess

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'

    parser = make_parser()

    # filename = sys.argv[1]
    filename = "Tests/palindrome.cl"

    with open(filename) as f:
            cool_program_code = f.read()

    parse_result = parser.parse(cool_program_code)
    type_scope = parse_result.typecheck()
    cgen = CGen(parse_result, type_scope)
    code = cgen.code_gen()

    assembly_name = os.path.splitext(basename(filename))[0] 
    with open("x86/" + assembly_name + ".s", 'w') as f:
        print("writing into file {}.s".format(assembly_name))
        f.write(code)


    print(subprocess.check_output(
        [
            "clang", 
            "runtime/runtime.c", 
            "runtime/startup.s", 
            "x86/{}.s".format(assembly_name),
            "-o",
            "bin/{}".format(assembly_name)

        ]))

    