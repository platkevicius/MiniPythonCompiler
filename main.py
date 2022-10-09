from lark import Lark
from argparse import ArgumentParser
from syntaxTree import converter
from mi import miGenerator

# read grammar from file
grammar_file = open("grammars/expressionGrammar.txt")
grammar = grammar_file.read()
grammar_file.close()

# initializing parser with lalr
language_parser = Lark(grammar, start="goal", parser="lalr", lexer="contextual")

# read script file from command line
argument_parser = ArgumentParser()
argument_parser.add_argument("-f", "--file", dest="filename",
                             help="choose script file for compilation")

args = argument_parser.parse_args()
filename = args.filename

# generate parse tree for script file
script_file = open(filename)
parse_tree = language_parser.parse(script_file.read())
script_file.close()

print(parse_tree.pretty())

# generate syntaxTree from parse tree
ast = converter.parse_tree_to_ast(parse_tree)

# code generation for target architecture (MI / RISC-V)
miGenerator.generateMachineCode(ast)
