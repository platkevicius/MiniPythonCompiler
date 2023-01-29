from lark import Lark
from argparse import ArgumentParser

from lark.indenter import Indenter

from mi.MiGenerator import MiGenerator
from riscv.RiscvAllocator import RiscvAllocator
from riscv.RiscvGenerator import RiscvGenerator
from mi.MiAllocator import MiAllocator
from shared.type import TypeCheck
from syntaxTree import Converter

# read grammar from file
grammar_file = open("shared/grammars/miniPythonGrammar.txt")
grammar = grammar_file.read()
grammar_file.close()


# initializing parser with lalr
class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8


language_parser = Lark(grammar, start="goal", parser="lalr", postlex=TreeIndenter())

# read script file from command line
argument_parser = ArgumentParser()
argument_parser.add_argument("-f", "--file", dest="filename",
                             help="choose script file for compilation")
argument_parser.add_argument("-a", "--architecture", dest="architecture",
                             help="choose target architecture to compile program to")

args = argument_parser.parse_args()
filename = args.filename
architecture = args.architecture

# generate parse tree for script file
script_file = open(filename)
parse_tree = language_parser.parse(script_file.read())
script_file.close()

# generate syntaxTree from parse tree
ast = Converter.parse_tree_to_ast(parse_tree)

# type check pass
TypeCheck.typePass(ast)

# code generation for target architecture (MI / RISC-V)
generated_code = []
gen = None

if architecture == 'mi':
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))
else:
    gen = RiscvGenerator(ast, RiscvAllocator(None, 0, 0))

generated_code = gen.generateMachineCode()

for line in generated_code:
    print(line)
