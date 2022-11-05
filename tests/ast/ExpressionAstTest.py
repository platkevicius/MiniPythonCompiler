import os

from mi.TestUtil import createAstForTest
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant


def ast_expr_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, 'grammars/expressionGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/expressions/expression1.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 1
    assert type(ast[0]) == BinaryOp, "Should be BinaryOP"

    assert type(ast[0].left) == BinaryOp, "Should be BinaryOP"
    assert type(ast[0].right) == BinaryOp, "Should be BinaryOP"


def ast_expr_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, 'grammars/expressionGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/expressions/expression2.txt')

    ast = createAstForTest(grammar, script)
    assert len(ast) == 1
    assert type(ast[0]) == BinaryOp, "Should be BinaryOP"

    assert type(ast[0].left) == BinaryOp, "Should be BinaryOP"
    assert type(ast[0].right) == Constant, "Should be a Constant"


if __name__ == '__main__':
    ast_expr_1()
    ast_expr_2()
