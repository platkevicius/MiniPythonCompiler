import os

from mi.TestUtil import createAstForTest
from syntaxTree.statement.ForStatement import ForStatement
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.statement.WhileStatement import WhileStatement


def ast_if_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/if1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 4

    assert type(ast[3]) == IfStatement

    assert len(ast[3].statements) == 4
    assert type(ast[3].statements[3]) == IfStatement


def ast_if_3():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/if3.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 5

    assert type(ast[3]) == IfStatement

    assert len(ast[3].statements) == 4
    assert len(ast[3].else_statements) == 3

    assert type(ast[3].statements[3]) == IfStatement
    assert len(ast[3].statements[3].else_statements) == 1

    assert type(ast[4]) == VariableCreation


def ast_for_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/for1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 6

    assert type(ast[4]) == ForStatement
    assert len(ast[4].statements) == 3

    assert type(ast[5]) == VariableCreation


def ast_while_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/while1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 6

    assert type(ast[4]) == WhileStatement
    assert len(ast[4].statements) == 4

    assert type(ast[5]) == VariableCreation


if __name__ == '__main__':
    ast_if_1()
    ast_if_3()
    ast_for_1()
    ast_while_1()
