

from parser import *
import cool_global as GLOBAL

if __name__ == "__main__":
    import sys, os, glob

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'       

    parser = make_parser() 

    for filename in os.listdir(test_folder):
        if filename.endswith('.cl'):
            file_path = test_folder + "/" + filename
            print("-------------------Testing parser with file {}-------------------".format(filename))
            with open(file_path, encoding='utf-8') as file:
                GLOBAL.typecheckError = False
                cool_program_code = file.read()
                parse_result = parser.parse(cool_program_code)
                if parse_result.typecheck():
                    if not GLOBAL.typecheckError:
                        print("successful")