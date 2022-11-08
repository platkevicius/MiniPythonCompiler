import os
import unittest

from mi.TestUtil import createAstForTest
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.statement.LoopStatement import LoopStatement


class StatementAstTest(unittest.TestCase):
    def test_ast_if_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/if1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 4)

        self.assertEqual(type(ast[3]), IfStatement)

        self.assertEqual(len(ast[3].statements), 4)
        self.assertEqual(type(ast[3].statements[3]), IfStatement)

    def test_ast_if_3(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/if3.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 5)

        self.assertEqual(type(ast[3]), IfStatement)

        self.assertEqual(len(ast[3].statements), 4)
        self.assertEqual(len(ast[3].else_statements), 3)

        self.assertEqual(type(ast[3].statements[3]), IfStatement)
        self.assertEqual(len(ast[3].statements[3].else_statements), 1)

        self.assertEqual(type(ast[4]), VariableCreation)

    def test_ast_for_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/for1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 7)

        self.assertEqual(type(ast[5]), LoopStatement)
        self.assertEqual(len(ast[5].statements), 4)

        self.assertEqual(type(ast[6]), VariableCreation)

    def test_ast_while_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/statements/while1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 6)

        self.assertEqual(type(ast[4]), LoopStatement)
        self.assertEqual(len(ast[4].statements), 4)

        self.assertEqual(type(ast[5]), VariableCreation)


if __name__ == '__main__':
    unittest.main()
