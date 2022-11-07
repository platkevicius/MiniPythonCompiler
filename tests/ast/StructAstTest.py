import os

from mi.TestUtil import createAstForTest
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve


def ast_struct_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 6

    assert type(ast[0]) == StructNode
    assert type(ast[1]) == StructNode

    assert type(ast[2]) == VariableCreation
    assert type(ast[2].value) == StructCreate

    assert type(ast[3]) == VariableCreation
    assert type(ast[3].value) == StructCreate

    assert type(ast[4]) == VariableCreation
    assert type(ast[4].value) == StructCreate

    assert type(ast[5]) == VariableCreation
    assert type(ast[5].value) == StructCreate


def ast_struct_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct2.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 9

    assert type(ast[0]) == StructNode

    assert type(ast[1]) == VariableCreation
    assert type(ast[1].value) == StructCreate

    assert type(ast[2]) == StructAssignment
    assert type(ast[3]) == StructAssignment

    assert type(ast[4]) == VariableCreation
    assert type(ast[4].value.right.left) == StructResolve

    assert type(ast[5]) == VariableCreation
    assert type(ast[5].value) == StructResolve

    assert type(ast[6]) == VariableCreation
    assert type(ast[7]) == VariableCreation
    assert type(ast[8]) == VariableCreation


if __name__ == '__main__':
    ast_struct_1()
    ast_struct_2()
