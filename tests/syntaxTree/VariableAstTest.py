import os
import unittest

from mi.TestUtil import createAstForTest
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation


class VariableAstTest(unittest.TestCase):
    def test_ast_var_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 3)

        self.assertEqual(type(ast[0]), VariableCreation)
        self.assertEqual(ast[0].type_def, 'int')
        self.assertEqual(type(ast[1]), VariableAssignment)

        self.assertEqual(type(ast[2]), VariableCreation)
        self.assertEqual(ast[2].type_def, 'boolean')

    def test_ast_var_2(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable2.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 15)

        for child in ast:
            self.assertEqual(type(child), VariableCreation)
            self.assertEqual(child.type_def, 'int')

        self.assertEqual(type(ast[14].value.left), VariableNode)

    def test_ast_var_3(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable3.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 2)

        self.assertEqual(type(ast[0]), VariableCreation)
        self.assertEqual(ast[0].type_def, 'int')
        self.assertEqual(type(ast[1]), VariableAssignment)

    def test_ast_var_4(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable4.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 1)

        self.assertEqual(type(ast[0]), VariableCreation)
        self.assertEqual(ast[0].type_def, 'boolean')

        assert ast[0].value.op == 'and'


if __name__ == '__main__':
    unittest.main()
