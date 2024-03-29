from shared.struct import StructDefinitions
from syntaxTree.arrays.ArrayAssignment import ArrayAssignment
from syntaxTree.arrays.ArrayCreate import ArrayCreate
from syntaxTree.arrays.ArrayResolve import ArrayResolve
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.function.FunctionCreate import FunctionCreate
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.ReturnStatement import ReturnStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.statement.LoopStatement import LoopStatement
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve


class Generator:

    def __init__(self, goals, scope):
        self.goals = goals
        self.scope = scope
        self.generated_code = []

    def generateMachineCode(self):
        pass

    def generate(self, ast, scope):
        if type(ast) is FunctionCreate:
            self.generateFunctionCreate(ast, scope)
        if type(ast) is FunctionCall:
            self.generateFunctionCall(ast, scope)
        if type(ast) is ReturnStatement:
            self.generateReturnStatement(ast, scope)
        if type(ast) is StructNode:
            self.generateStruct(ast)
        if type(ast) is StructCreate:
            self.generateStructCreate(ast)
        if type(ast) is StructAssignment:
            self.generateStructAssignment(ast, scope)
        if type(ast) is StructResolve:
            self.generateStructResolve(ast, scope)
        if type(ast) is LoopStatement:
            self.generateLoopStatement(ast, scope)
        if type(ast) is IfStatement:
            self.generateIfStatement(ast, scope)
        if type(ast) is ArrayCreate:
            self.generateArrayCreate(ast, scope)
        if type(ast) is ArrayAssignment:
            self.generateArrayAssignment(ast, scope)
        if type(ast) is ArrayResolve:
            self.generateArrayResolve(ast, scope)
        if type(ast) is VariableCreation:
            self.generateVariableCreation(ast, scope)
        if type(ast) is VariableAssignment:
            self.generateVariableAssignment(ast, scope)
        elif type(ast) is BinaryOp:
            self.generateBinaryOp(ast, scope)
        elif type(ast) is Constant:
            self.generateConstant(ast)
        elif type(ast) is VariableNode:
            self.generateResolveVariable(ast, scope)

    def generateFunctionCreate(self, ast, scope):
        pass

    def generateFunctionCall(self, ast, scope):
        pass

    def generateReturnStatement(self, ast, scope):
        pass

    def generateStruct(self, ast):
        StructDefinitions.addDefinition(ast)

    def generateStructCreate(self, ast):
        pass

    def generateStructAssignment(self, ast, scope):
        pass

    def generateStructResolve(self, ast, scope):
        pass

    def generateLoopStatement(self, ast, scope):
        pass

    def generateIfStatement(self, ast, scope):
        pass

    def generateArrayCreate(self, ast, scope):
        pass

    def generateVariableCreation(self, ast, scope):
        pass

    def generateVariableAssignment(self, ast, scope):
        pass

    def generateBinaryOp(self, ast, scope):
        pass

    def generateConstant(self, ast):
        pass

    def generateResolveVariable(self, ast, scope):
        pass

    def generateInit(self):
        pass

    def generateHeap(self):
        pass

    def generateArrayAssignment(self, ast, scope):
        pass

    def generateArrayResolve(self, ast, scope):
        pass
