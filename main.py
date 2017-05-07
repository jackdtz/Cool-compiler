

from src.parser import *
import src.cool_global as GLOBAL
from src.cool_codegen import *

if __name__ == "__main__":
    import sys
    import os
    import glob
    from os.path import basename
    import subprocess


    parser = make_parser()

    filename = sys.argv[1]
    # filename = "Tests/let.cl"

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


    subprocess.run(
        [
            "clang", 
            "runtime/runtime.c", 
            "runtime/startup.s", 
            "x86/{}.s".format(assembly_name),
            "-o",
            "bin/{}".format(assembly_name)

        ])

    # subprocess.run(
    #     [
    #         "./bin/{}".format(assembly_name)
    #     ]
    # )