from lark import Lark
from lark.indenter import Indenter

from syntaxTree import Converter


def createAstForTest(grammar_location, script_location):
    # read grammar from file
    grammar_file = open(grammar_location)
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

    # generate parse tree for script file
    script_file = open(script_location)
    parse_tree = language_parser.parse(script_file.read())
    script_file.close()

    # generate syntaxTree from parse tree
    return Converter.parse_tree_to_ast(parse_tree)
