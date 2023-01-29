import os

from mi.TestUtil import createAstForTest
from shared.type import TypeCheck


def type_valid_struct_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct1.txt')

    ast = createAstForTest(grammar, script)
    TypeCheck.typePass(ast)


def type_valid_struct_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct2.txt')

    ast = createAstForTest(grammar, script)
    TypeCheck.typePass(ast)


if __name__ == '__main__':
    type_valid_struct_1()
    type_valid_struct_2()
