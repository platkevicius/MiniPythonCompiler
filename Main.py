from lark import Lark
from argparse import ArgumentParser

from riscv import RiscvGenerator
from shared.allocation.DataAllocator import DataAllocator
from syntaxTree import Converter
from mi import MiGenerator

# read grammar from file
grammar_file = open("shared/grammars/expressionGrammar.txt")
grammar = grammar_file.read()
grammar_file.close()

# initializing parser with lalr
language_parser = Lark(grammar, start="goal", parser="lalr", lexer="contextual")

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

# code generation for target architecture (MI / RISC-V)
generated_code = []
if architecture == 'mi':
    generated_code = MiGenerator.generateMachineCode(ast, DataAllocator(None, 0, 0))
else:
    generated_code = RiscvGenerator.generateMachineCode(ast, DataAllocator(None, 0, 0))

for line in generated_code:
    print(line)
