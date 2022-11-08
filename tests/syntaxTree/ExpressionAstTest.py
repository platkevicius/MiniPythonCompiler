import os
import unittest

from mi.TestUtil import createAstForTest
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant


class ExpressionAstTest(unittest.TestCase):
    def test_ast_expr_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/expressionGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/expressions/expression1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 1)
        self.assertEqual(type(ast[0]), BinaryOp)

        self.assertEqual(type(ast[0].left), BinaryOp)
        self.assertEqual(type(ast[0].right), BinaryOp)

    def test_ast_expr_2(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/expressionGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/expressions/expression2.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 1)
        self.assertEqual(type(ast[0]), BinaryOp)

        self.assertEqual(type(ast[0].left), BinaryOp)
        self.assertEqual(type(ast[0].right), Constant)


if __name__ == '__main__':
    unittest.main()
