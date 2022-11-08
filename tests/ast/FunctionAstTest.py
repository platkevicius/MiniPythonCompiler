import os

from mi.TestUtil import createAstForTest
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.ReturnStatement import ReturnStatement
from syntaxTree.statement.VariableCreation import VariableCreation


def ast_function_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/functions/function1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 1
    assert len(ast[0].params_list) == 1
    assert ast[0].return_type == 'int'
    assert len(ast[0].statements) == 4

    assert type(ast[0].statements[0]) == IfStatement
    assert type(ast[0].statements[1]) == IfStatement
    assert type(ast[0].statements[2]) == IfStatement
    assert type(ast[0].statements[3]) == ReturnStatement


def ast_function_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/functions/function2.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 2
    assert len(ast[0].params_list) == 3
    assert ast[0].return_type == 'int'
    assert len(ast[0].statements) == 1

    assert type(ast[0].statements[0]) == ReturnStatement
    assert type(ast[1]) == VariableCreation
    assert type(ast[1].value) == FunctionCall


if __name__ == '__main__':
    ast_function_1()
    ast_function_2()
