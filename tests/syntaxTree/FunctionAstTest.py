import os
import unittest

from mi.TestUtil import createAstForTest
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.ReturnStatement import ReturnStatement
from syntaxTree.statement.VariableCreation import VariableCreation


class FunctionAstTest(unittest.TestCase):
    def test_ast_function_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/functions/function1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 1)
        self.assertEqual(len(ast[0].params_list), 1)
        self.assertEqual(ast[0].return_type, 'int')
        self.assertEqual(len(ast[0].statements), 4)

        self.assertEqual(type(ast[0].statements[0]), IfStatement)
        self.assertEqual(type(ast[0].statements[1]), IfStatement)
        self.assertEqual(type(ast[0].statements[2]), IfStatement)
        self.assertEqual(type(ast[0].statements[3]), ReturnStatement)

    def test_ast_function_2(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/functions/function2.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 2)
        self.assertEqual(len(ast[0].params_list), 3)
        self.assertEqual(ast[0].return_type, 'int')
        self.assertEqual(len(ast[0].statements), 1)

        self.assertEqual(type(ast[0].statements[0]), ReturnStatement)
        self.assertEqual(type(ast[1]), VariableCreation)
        self.assertEqual(type(ast[1].value), FunctionCall)


if __name__ == '__main__':
    unittest.main()
