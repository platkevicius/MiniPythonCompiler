import os.path
import subprocess
import unittest

from mi.MiGenerator import generateMachineCode
from mi.allocation.DataAllocator import DataAllocator
from tests.mi.TestUtil import createAstForTest
from tests.util.ProgramExecuter import execute_java


class ExpressionTest(unittest.TestCase):

    @staticmethod
    def test_generate_arithmetic_expression():
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, 'grammars/expressionGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/example1.txt')
        output = os.path.join(os.path.dirname(__file__), 'output/Arithmetic1.txt')
        program = os.path.join(os.path.dirname(__file__), 'mi-simulator-1.11.jar')

        ast = createAstForTest(grammar, script)
        code = generateMachineCode(ast, DataAllocator())

        file = open(r'' + output, "w")
        for line in code:
            file.write(line)
            file.write('\n')
        file.close()

        execute_java(r'' + program, output)


if __name__ == '__main__':
    unittest.main()
