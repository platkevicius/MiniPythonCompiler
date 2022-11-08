import os
import unittest

from mi.TestUtil import createAstForTest
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve


class StructAstTest(unittest.TestCase):
    def test_ast_struct_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct1.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 6)

        self.assertEqual(type(ast[0]), StructNode)
        self.assertEqual(type(ast[1]), StructNode)

        self.assertEqual(type(ast[2]), VariableCreation)
        self.assertEqual(type(ast[2].value), StructCreate)

        self.assertEqual(type(ast[3]), VariableCreation)
        self.assertEqual(type(ast[3].value), StructCreate)

        self.assertEqual(type(ast[4]), VariableCreation)
        self.assertEqual(type(ast[4].value), StructCreate)

        self.assertEqual(type(ast[5]), VariableCreation)
        self.assertEqual(type(ast[5].value), StructCreate)

    def test_ast_struct_2(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/structs/struct2.txt')

        ast = createAstForTest(grammar, script)
        self.assertEqual(len(ast), 9)

        self.assertEqual(type(ast[0]), StructNode)

        self.assertEqual(type(ast[1]), VariableCreation)
        self.assertEqual(type(ast[1].value), StructCreate)

        self.assertEqual(type(ast[2]), StructAssignment)
        self.assertEqual(type(ast[3]), StructAssignment)

        self.assertEqual(type(ast[4]), VariableCreation)
        self.assertEqual(type(ast[4].value.right.left), StructResolve)

        self.assertEqual(type(ast[5]), VariableCreation)
        self.assertEqual(type(ast[5].value), StructResolve)

        self.assertEqual(type(ast[6]), VariableCreation)
        self.assertEqual(type(ast[7]), VariableCreation)
        self.assertEqual(type(ast[8]), VariableCreation)


if __name__ == '__main__':
    unittest.main()
