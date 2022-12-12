import os
import unittest

from mi.MiGenerator import MiGenerator
from mi.TestUtil import createAstForTest
from mi.MiAllocator import MiAllocator


def type_valid_variable_1():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable1.txt')

    ast = createAstForTest(grammar, script)
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))

    gen.generateMachineCode()


def type_valid_variable_2():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable2.txt')

    ast = createAstForTest(grammar, script)
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))

    gen.generateMachineCode()


def type_valid_variable_3():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable3.txt')

    ast = createAstForTest(grammar, script)
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))

    gen.generateMachineCode()


def type_valid_variable_4():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable4.txt')

    ast = createAstForTest(grammar, script)
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))

    gen.generateMachineCode()


def type_valid_variable_5():
    grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
    script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable5.txt')

    ast = createAstForTest(grammar, script)
    gen = MiGenerator(ast, MiAllocator(None, 0, 0))

    gen.generateMachineCode()


class VariableTypeTest(unittest.TestCase):
    def test_invalid_variable_1(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable1.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))
        self.assertRaises(ValueError, gen.generateMachineCode)

    def test_invalid_variable_2(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable2.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))
        self.assertRaises(ValueError, gen.generateMachineCode)

    def test_invalid_variable_3(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable3.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))
        self.assertRaises(ValueError, gen.generateMachineCode)

    def test_invalid_variable_4(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable4.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))
        self.assertRaises(ValueError, gen.generateMachineCode)

    def test_invalid_variable_5(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable5.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))
        self.assertRaises(ValueError, gen.generateMachineCode)

    def test_invalid_variable_6(self):
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/invalid/variables/variable6.txt')

        ast = createAstForTest(grammar, script)
        gen = MiGenerator(ast, MiAllocator(None, 0, 0))

        self.assertRaises(ValueError, gen.generateMachineCode)


if __name__ == '__main__':
    type_valid_variable_1()
    type_valid_variable_2()
    type_valid_variable_3()
    type_valid_variable_4()
    type_valid_variable_5()

    unittest.main()
