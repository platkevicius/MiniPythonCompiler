import os.path
import subprocess
import unittest

from mi.MiGenerator import MiGenerator
from shared.allocation.DataAllocator import DataAllocator
from tests.mi.TestUtil import createAstForTest


class VariableTest(unittest.TestCase):

    @staticmethod
    def test_generate_arithmetic_expression():
        grammar = os.path.join(os.path.dirname(__file__), os.pardir, '../shared/grammars/miniPythonGrammar.txt')
        script = os.path.join(os.path.dirname(__file__), os.pardir, 'examples/valid/variables/variable1.txt')
        output = os.path.join(os.path.dirname(__file__), 'output/Variable1.txt')
        program = os.path.join(os.path.dirname(__file__), 'mi-simulator-cli-1.11.jar')

        ast = createAstForTest(grammar, script)
        code = MiGenerator(ast, DataAllocator(None, 0, 0)).generateMachineCode()

        file = open(r'' + output, "w")
        for line in code:
            file.write(line)
            file.write('\n')
        file.close()

        result = subprocess.check_output(["java", "-jar", program, output], shell=True)

        for line in result:
            print(line)


if __name__ == '__main__':
    unittest.main()
