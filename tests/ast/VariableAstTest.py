import os

from mi.TestUtil import createAstForTest
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation


def ast_var_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 4

    assert type(ast[0]) == VariableCreation
    assert ast[0].type_def == 'int'
    assert type(ast[1]) == VariableAssignment

    assert type(ast[2]) == VariableCreation
    assert ast[2].type_def == 'boolean'
    assert type(ast[3]) == VariableAssignment


def ast_var_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable2.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 15

    for child in ast:
        assert type(child) == VariableCreation
        assert child.type_def == 'int'

    assert type(ast[14].value.left) == VariableNode


def ast_var_3():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable3.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 2

    assert type(ast[0]) == VariableCreation
    assert ast[0].type_def == 'int'
    assert type(ast[1]) == VariableAssignment


def ast_var_4():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable4.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 1

    assert type(ast[0]) == VariableCreation
    assert ast[0].type_def == 'boolean'

    assert ast[0].value.op == 'and'


if __name__ == '__main__':
    ast_var_1()
    ast_var_2()
    ast_var_3()
    ast_var_4()
