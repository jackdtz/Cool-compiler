from cool_ast import *
from cool_global import *


class CGen(object):

    tag = 0
    wordsize = 8

    def __init__(self, program: 'Program'):
        self.program = program
        self.classTable = {}
        self.dispatchTable = {}
        self.inttable = {}
        self.stringtable = {}
        self.booltable = {}
        self.asm = []
        self.runtime_funs = ['print_string']
        self.tag = 0

    def genTag(self):
        # generate prime number for class tag
        self.tag += 1
        return self.tag

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
                FeatureMethodDecl('int_string', [], 'String', None),
                FeatureMethodDecl('in_int', [], 'Int', None)
            ]
        )

        IntClass = Class('Int', [FeatureAttribute('value', 'Int', Integer(0))])

        BoolClass = Class('Bool', [FeatureAttribute('value', 'Bool', Boolean(False))])

        StringClass = Class(
            'String',
            [
                
                FeatureMethodDecl('length', [], 'Int', None),
                FeatureMethodDecl('concat', [FormalParam('s', 'String')], 'String', None),
                FeatureMethodDecl('substr', [FormalParam('i', 'Int'), FormalParam('l', 'Int')], 'String', None),
                FeatureAttribute('size', 'Int', Integer(0)),
                FeatureAttribute('value', 'String', String(""))
            ]
        )

        return [ObjectClass, IOClass, StringClass, IntClass, BoolClass]


    def genGlobalData(self):

        ret = ""

        ret += ".data" + NEWLINE

        # generate prototype objects

        prototypes = {}
        for c in self.getPredeinedClasses():
            prototype = []
            label = c.className + UNDERSCORE + PROTOTYPE_SUFFIX
            prototype.append(self.genTag())         # tag

            attributes = [f for f in c.features if isinstance(f, FeatureAttribute)]
            prototype.append(len(attributes) + 1)   # size


            dispatchTab_lab = c.className + UNDERSCORE + DISPATCH_TABLE
            prototype.append(dispatchTab_lab)

            
            for att in attributes:
                if att.decType == 'Int':
                    if not att.init:
                        prototype.append(0)
                    else:
                        prototype.append(att.init.ival)
                elif att.decType == 'Bool':
                    if not att.init:
                        prototype.append(0)
                    else:
                        prototype.append(1 if att.init.bval else 0)
                elif att.decType == 'String':
                    if not att.init:
                        prototype.append("") # string
                    else:
                        prototype.append("\"" + att.init.sval + "\"")
                
            
            prototypes[label] = prototype

        for label, values in prototypes.items():
            value_str =  NEWLINE.join([TAB + WORD + TAB + str(v) for v in values])
            ret += NEWLINE + label + COLON + NEWLINE + value_str + NEWLINE



        return ret  


    # def generate_classTable(self):

    #     # generate prototype objects 
    #     for c in self.program.classes:
    #         className = c.className
    #         label_name = className + PREFIX + PROTOTYPE_SUFFIX
    #         tag = self.genTag()



            
            






    def cgen_program(self, program: 'Program'):


        self.generate_classTable()

        for c in program.classes:
            attributes = [self.cgen_attr(f) for f in c.features if isinstance(f, FeatureAttribute)]
            objModel = Model()
            objModel.tag = CGen.tag
            CGen.tag += 1

            objModel.size = 3 + len(attributes)
            objModel.attributes = attributes
            objModel.vtable = []

            self.classTable[c.className] = objModel

        for c in program.classes:
            self.cgen_class(c)


    def cgen_attr(self, attr):
        if not attr.init:
            return (attr.id, 0)
        
        return (attr.id, self.cgen_exp(attr.init))



    def cgen_class(self, c: 'Class'):
        objModel = self.classTable[c.className]

        if c.inheritType:
            parentObjModel = self.classTable[c.inheritType]
        else:
            parentObjModel = self.classTable['Object']

        objModel.size += len(parentObjModel.attributes) 
        objModel.attributes = parentObjModel.arrtibutes + objModel.attributes

        methods = [m for m in c.features if isinstance(m, FeatureMethodDecl)]

        for method in methods:
            self.cgen_methodDecl(method, objModel)

    def cgen_methodDecl(self, method: 'FeatureMethodDecl'):

        local_table = {}

        ret = "{}: \n".format(str(method.methodName))

        ret += "\t pushq %rbp \n"
        ret += "\t movq %rsp, %rbp \n"

        num_locals = len(method.formalParams) + 1
        params_name = [f.id for f in method.formalParams]

        ret += "\t subq {}, %rsp \n".format(str(num_locals * CGen.wordsize))

        for i, id in enumerate(params_name):
            local_offset = -(i * CGen.wordsize)
            local_table[id] = local_offset
            ret += "\t movq {}(%rbp), %rax \n".format(str(16 + i * CGen.wordsize))
            ret += "\t movq %rax, -{}(%rbp) \n".format(str(local_offset))

        ret += self.cgen_exp(method.bodyExpr, local_table)

        ret += "\t leave \n"
        ret += "\t ret \n"

        return ret
    
    def cgen_exp(self, exp: 'Expr', local_table):
        if isinstance(exp, AssignmentExpr):
            return self.cgen_assignment(exp, local_table)


    # def cgen_assignment(self, exp, local_table):
    #     left = exp.id
    #     right = self.cgen_exp(exp.expr, local_table)

    #     ret = ""

    #     # local varible
    #     if left in local_table:
    #         ret += "\t movq %rax, {}(%rbp) \n".format(local_table[left])
    #     else:
            # attribute




    # def cgen_arith(self, exp):

    #     if isinstance(exp, Plus):
    #         op = "addq"
    #     elif isinstance(exp, Minus):
    #         op = "subq"
    #     elif isinstance(exp, Multiply):
    #         op = "imul"
    #     elif isinstance(exp, Divide):
    #         op = "idiv"


    #     if not isinstance(exp, Divide):

    #         return """
    #             {e1}
    #             movq %rax, %rbx
    #             {e2}
    #             {op} %rbx, %rax
    #         """.format(e1=self.cgen_exp(exp.e1), e2=self.cgen_exp(exp.e2), op=op)
    

        


        




            


if __name__ == "__main__":
    cgen = CGen(None)
    ret = cgen.genGlobalData()
    print(ret)

        
        
        


        


        