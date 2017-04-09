from cool_ast import *
from cool_global import *
from collections import OrderedDict


class CGen(object):

    def __init__(self, program: 'Program'):
        self.program = program
        self.inttable = {}
        self.stringtable = {}
        self.booltable = {}
        self.tag = -1
        self.attrtable = {}
        self.wordsize = 8

        self.prototypes = OrderedDict()
        self.dispatchTable = {}
        self.classObjTab = []
        

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
        ret += ".data" + NEWLINE

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
            self.dispatchTable[c.className] = [c.className + DOT + m.methodName for m in methodDecls] 


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

                self.attrtable[c.className][attr.id] = (i + 3) * self.wordsize
                
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
        ret = self.genGlobalData()

        return ret


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
    

        
        
        


        


        