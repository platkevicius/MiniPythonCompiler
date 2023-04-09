from mi.FunctionEnvironment import FunctionEnvironment
from mi.MiAllocator import *
from shared.Generator import Generator
from shared.SymbolGenerator import createNewSymbol
from shared.function import FunctionDefinitions
from shared.function.Function import Function
from shared.struct import StructDefinitions
from shared.type import TypeResolver
from shared.variables.Variable import Variable
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.function.FunctionCreate import FunctionCreate
from syntaxTree.struct.StructNode import StructNode


class MiGenerator(Generator):
    def __init__(self, goals, scope):
        super().__init__(goals, scope)

    def generateMachineCode(self):
        definitions = []
        for goal in self.goals:
            if type(goal) is FunctionCreate or type(goal) is StructNode:
                definitions.append(goal)

        self.generated_code.append(self.generateInit())

        self.generated_code.append('JUMP start')

        self.generated_code.append(self.intToIEEEFloatMethod())
        self.generated_code.append(self.arrayIndexLocation())

        for definition in definitions:
            self.generate(definition, self.scope)

        self.generated_code.append('start:')
        self.goals = [x for x in self.goals if x not in definitions]
        for goal in self.goals:
            self.generate(goal, self.scope)
        self.generated_code.append('HALT')
        self.generated_code.append(self.generateHeap())
        return self.generated_code

    def generateFunctionCreate(self, ast, scope):
        name = ast.name
        return_type = ast.return_type
        params = ast.params_list

        FunctionDefinitions.addDefinition(Function(name, params, return_type))

        param_scope = FunctionEnvironment(scope)

        for param in ast.params_list:
            param_scope.addParam(param)
        param_scope.addParam(Variable('return', return_type))

        body_scope = FunctionEnvironment(param_scope)
        self.generated_code.append(name + ': ')
        self.generated_code.append('PUSHR')
        self.generated_code.append('MOVE W SP, R11')
        for statement in ast.statements:
            self.generate(statement, body_scope)

    def generateFunctionCall(self, ast, scope):
        function = FunctionDefinitions.findDefinition(ast.name)

        if len(function.params) != len(ast.params):
            raise ValueError('param size is not equivalent')

        # free space for type
        if function.return_type is not None:
            lop = self.getSpaceForType(function.return_type)
            self.generated_code.append(f'CLEAR {lop} -!SP')  # todo: type needs to be added

        for i in range(len(function.params) - 1, -1, -1):
            expr = ast.params[i]
            self.generate(expr, scope)

        self.generated_code.append(f'CALL {function.name}')
        self.generated_code.append(f'ADD W I {len(function.params) * 4}, SP')

    def generateReturnStatement(self, ast, scope):
        return_data = scope.findData('return')
        lop = self.getSpaceForType(return_data.data.type_def)
        offset = str(return_data.offset * 4)

        self.generate(ast.expression, scope)

        self.generated_code.append(f'MOVE {lop} !SP+, {offset}+!R11')
        self.generated_code.append('MOVE W R11, SP')  # reset Stack Pointer
        self.generated_code.append('POPR')
        self.generated_code.append('RET')

    def generateStructCreate(self, struct):
        self.generated_code.append('MOVE W hp, R13')

        offset = 0
        for definition in StructDefinitions.findDefinition(struct.name):
            offset += StructDefinitions.getOffsetForType(definition.type_def)

        self.generated_code.append(f'ADD W I {offset}, hp')
        self.generated_code.append('MOVE W R13, -!SP')

    def generateStructAssignment(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        self.generate(struct.value, scope)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        variable_offset = str(variable.offset)
        relative_register = self.getRelativeRegister(scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'MOVE {lop} !SP+, {attr_offset}+!R{variable_offset}')
            case Location.STACK:
                self.generated_code.append(f'MOVE W {variable.offset * 4}+!{relative_register}, R10')
                self.generated_code.append(f'MOVE {lop} !SP+, {attr_offset}+!R10')

    def generateStructResolve(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        variable_offset = str(variable.offset)
        relative_register = self.getRelativeRegister(scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'MOVE {lop} {attr_offset}+!R{variable_offset}, -!SP')
            case Location.STACK:
                self.generated_code.append(f'MOVE W {variable.offset * 4}+!{relative_register}, R10')
                self.generated_code.append(
                    f'MOVE {lop} {attr_offset}+!R10, -!SP')

    def generateLoopStatement(self, while_statement, scope):
        local_scope = MiAllocator(scope, scope.dataInRegister, scope.dataInStack)
        while_symbol = createNewSymbol('while')
        continue_symbol = createNewSymbol('continue')

        self.generated_code.append('')  # formatting
        self.generated_code.append(while_symbol + ':')
        self.generate(while_statement.condition, local_scope)

        self.generated_code.append('ADD W I 4, SP')  # reset Stack Pointer from logical calculation in Stack
        self.generated_code.append('CMP W I 1, -4+!SP')
        self.generated_code.append('JNE ' + continue_symbol)

        for statement in while_statement.statements:
            self.generate(statement, local_scope)

        self.generated_code.append(f'ADD W I {local_scope.getOffsetForLocalVariable() * 4}, SP')  # reset Stack Pointer
        self.generated_code.append('JUMP ' + while_symbol)

        self.generated_code.append('')  # formatting
        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append(f'ADD W I {local_scope.getOffsetForLocalVariable() * 4}, SP')  # reset Stack Pointer

    def generateIfStatement(self, if_statement, scope):
        local_scope = MiAllocator(scope, scope.dataInRegister, scope.dataInStack)
        else_symbol = createNewSymbol('else')
        continue_symbol = createNewSymbol('continue')

        has_else = len(if_statement.else_statements) != 0

        self.generate(if_statement.condition, scope)
        self.generated_code.append('ADD W I 4, SP')  # reset Stack Pointer from logical calculation in Stack
        self.generated_code.append('CMP W I 1, -4+!SP')
        self.generated_code.append('JNE ' + (else_symbol if has_else else continue_symbol))

        self.generated_code.append('')  # formatting
        for statement in if_statement.statements:
            self.generate(statement, local_scope)

        if has_else:
            self.generated_code.append(f'JUMP {continue_symbol}')
            self.generated_code.append(else_symbol + ': ')
            for statement in if_statement.else_statements:
                self.generate(statement, local_scope)

        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append(f'ADD W I {local_scope.getOffsetForLocalVariable() * 4}, SP')  # reset Stack Pointer

    def generateArrayCreate(self, ast, scope):
        self.generated_code.append('MOVE W hp, R13')

        self.generated_code.append(f'ADD W I {4 * (len(ast.dimensions) + 3)}, hp')
        self.generated_code.append(f'MOVE W I {len(ast.dimensions)}, !R13')
        binOps = []
        counter = 1
        for i in range(len(ast.dimensions)):
            dimension = ast.dimensions[i]
            op = BinaryOp(dimension, '*', None)
            if i == len(ast.dimensions) - 2:
                op.right = ast.dimensions[i + 1]
            if i != len(ast.dimensions) - 1:
                binOps.append(op)
            self.generate(dimension, scope)
            self.generated_code.append(f'MOVE W !SP+, {4 * counter}+!R13')
            counter += 1
        self.generated_code.append(f'MOVE W I 4, {4 * counter}+!R13')  # TODO: lop needs to be changed
        counter += 1
        self.generated_code.append(f'ADD W I 4, hp, {4 * counter}+!R13')  # basis address of array todo, change to use R13!
        for i in reversed(range(len(binOps) - 1, 0, -1)):
            op1 = binOps[i]
            op2 = binOps[i - 1]
            op2.right = op1
            binOps[i - 1] = op2

        self.generate(binOps[0], scope)
        self.generated_code.append('ADD W !SP+, hp')
        self.generated_code.append('MOVE W R13, -!SP')

    def generateArrayAssignment(self, ast, scope):
        self.generated_code.append('MOVE W hp, R13')
        self.generated_code.append(f'ADD W I {4 * len(ast.index_expr)}, hp')
        counter = 0
        for index in ast.index_expr:
            self.generate(ast.index_expr[index], scope)
            self.generated_code.append(f'MOVE W !SP+, {4 * counter}+!R13')
            counter += 1

        variable = scope.findData(ast.name)
        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('CLEAR W -!SP')
                self.generated_code.append('MOVE W R13, -!SP')
                self.generated_code.append(f'MOVE W R{variable.offset}, -!SP')
                self.generated_code.append('CALL arrayLocation')
                self.generated_code.append('ADD W I 8, SP')
                self.generate(ast.value_expr, scope)
                self.generated_code.append('MOVE W !SP, !(4+!SP)')
                self.generated_code.append('ADD W I 4, SP')
            case Location.STACK:
                relative_register = self.getRelativeRegister(scope)
                self.generated_code.append('CLEAR W -!SP')
                self.generated_code.append('MOVE W R13, -!SP')
                self.generated_code.append(f'MOVE W {variable.offset * 4}+!{relative_register}, -!SP')
                self.generated_code.append('CALL arrayLocation')
                self.generated_code.append('ADD W I 8, SP')
                self.generate(ast.value_expr, scope)
                self.generated_code.append('MOVE W !SP, !(4+!SP)')
                self.generated_code.append('ADD W I 4, SP')

    def generateArrayResolve(self, ast, scope):
        self.generated_code.append('MOVE W hp, R13')
        self.generated_code.append(f'ADD W I {4 * len(ast.dimensions)}, hp')
        counter = 0
        for index in ast.dimensions:
            self.generate(ast.dimensions[index], scope)
            self.generated_code.append(f'MOVE W !SP+, {4 * counter}+!R13')
            counter += 1

        variable = scope.findData(ast.name)
        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('CLEAR W -!SP')
                self.generated_code.append('MOVE W R13, -!SP')
                self.generated_code.append(f'MOVE W R{variable.offset}, -!SP')
                self.generated_code.append('CALL arrayLocation')
                self.generated_code.append('ADD W I 8, SP')
                self.generated_code.append('MOVE W !!SP, !SP')
            case Location.STACK:
                relative_register = self.getRelativeRegister(scope)
                self.generated_code.append('CLEAR W -!SP')
                self.generated_code.append('MOVE W R13, -!SP')
                self.generated_code.append(f'MOVE W {variable.offset * 4}+!{relative_register}, -!SP')
                self.generated_code.append('CALL arrayLocation')
                self.generated_code.append('ADD W I 8, SP')
                self.generated_code.append('MOVE W !!SP, !SP')

    def generateVariableCreation(self, variable_creation, scope):
        name = variable_creation.name
        type_def = variable_creation.type_def
        self.generate(variable_creation.value, scope)
        variable = scope.addData(Variable(name, type_def))

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'MOVE {self.getSpaceForType(type_def)} !SP, R{variable.offset}')
                self.generated_code.append('ADD W I 4, SP')

    def generateVariableAssignment(self, variable_assignment, scope):
        name = variable_assignment.name
        self.generate(variable_assignment.value, scope)
        variable = scope.findData(name)
        type_def = variable.data.type_def
        lop = self.getSpaceForType(type_def)

        relative_register = self.getRelativeRegister(scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'MOVE {lop} !SP, R{variable.offset}')
            case Location.STACK:
                self.generated_code.append(f'MOVE {lop} !SP, {variable.offset * 4}+!{relative_register}')

        self.generated_code.append('ADD W I 4, SP')

    def generateResolveVariable(self, variable, scope):
        variable = scope.findData(variable.name)
        type_def = variable.data.type_def
        lop = self.getSpaceForType(type_def)

        relative_register = self.getRelativeRegister(scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'MOVE {lop} R{variable.offset}, -!SP')
            case Location.STACK:
                self.generated_code.append(f'MOVE {lop} {variable.offset * 4}+!{relative_register}, -!SP')

    def generateBinaryOp(self, binary_op, scope):
        type_def = TypeResolver.resolveType(binary_op, scope)
        type_expr1 = TypeResolver.resolveType(binary_op.left, scope)
        type_expr2 = TypeResolver.resolveType(binary_op.right, scope)

        self.generate(binary_op.left, scope)
        if (type_expr1 == 'int' and type_def == 'float') or \
                (type_expr1 == 'int' and type_expr2 == 'float'):
            self.generated_code.append('MOVE W !SP, -4+!SP')
            self.generated_code.append('CLEAR W !SP')
            self.generated_code.append("SUB W I 4, SP")
            self.generated_code.append('CALL convertToIEEE754')
            self.generated_code.append('ADD W I 4, SP')
            type_expr1 = 'float'

        self.generate(binary_op.right, scope)
        if (type_expr2 == 'int' and type_def == 'float') or \
                (type_expr2 == 'int' and type_def == 'float'):
            self.generated_code.append('MOVE W !SP, -4+!SP')
            self.generated_code.append('CLEAR W !SP')
            self.generated_code.append("SUB W I 4, SP")
            self.generated_code.append('CALL convertToIEEE754')
            self.generated_code.append('ADD W I 4, SP')

        op = binary_op.op
        lop = self.getSpaceForType(type_expr1)
        match op:
            case '+':
                self.generated_code.append(f'ADD {lop} !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')
            case '-':
                self.generated_code.append(f'SUB {lop} !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')
            case '*':
                self.generated_code.append(f'MULT {lop} !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')
            case '/':
                self.generated_code.append(f'DIV {lop} !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')
            case '>':
                self.generateComparison('>', lop)
            case '>=':
                self.generateComparison('>=', lop)
            case '==':
                self.generateComparison('==', lop)
            case '<=':
                self.generateComparison('<=', lop)
            case '<':
                self.generateComparison('<', lop)
            case 'or':
                self.generated_code.append(f'OR W !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')
            case 'and':
                self.generated_code.append(f'MULT W !SP, 4+!SP')
                self.generated_code.append(f'ADD W I 4, SP')

    def generateComparison(self, op, lop):
        mappings = {">": "JGT",
                    ">=": "JGE",
                    "==": "JEQ",
                    "<=": "JLE",
                    "<": "JLT"}
        symbol = createNewSymbol('logicalTrue')
        symbol_continue = createNewSymbol('continue')

        self.generated_code.append(f'SUB {lop} !SP, 4+!SP')
        self.generated_code.append(f'ADD W I 4, SP')
        self.generated_code.append(f'CMP {lop} !SP, I 0')
        self.generated_code.append(f'{mappings.get(op)} {symbol}')
        self.generated_code.append(f'MOVE W I 0, !SP')
        self.generated_code.append(f'JUMP {symbol_continue}')
        self.generated_code.append('')
        self.generated_code.append(f'{symbol}:')
        self.generated_code.append(f'MOVE W I 1, !SP')
        self.generated_code.append('')
        self.generated_code.append(f'{symbol_continue}:')

    def generateConstant(self, constant):
        if constant.value == 'true':
            self.generated_code.append('MOVE W I 1, -!SP')
        elif constant.value == 'false':
            self.generated_code.append('MOVE W I 0, -!SP')
        else:
            if type(constant.value) == int:
                self.generated_code.append(f'MOVE W I {constant.value}, -!SP')
            else:
                self.generated_code.append(f'MOVE F I {constant.value}, -!SP')

    def generateInit(self):
        return '''
SEG
MOVE W I H'10000', SP
MOVE W I H'10000', R12
MOVEA heap, hp
    '''

    def generateHeap(self):
        return '''
hp: RES 4
heap: RES 0'''

    def getSpaceForType(self, type_def):
        match type_def:
            case 'int':
                return 'W'
            case 'float':
                return 'F'
            case _:
                return 'W'

    def getRelativeRegister(self, scope):
        match scope.isInFunction():
            case False:
                return 'R12'
            case True:
                return 'R11'

    def intToIEEEFloatMethod(self):
        return '''
count:
PUSHR
MOVE W SP, R13
CLEAR W R0

while:
CMP W 64+!R13, I 1
JEQ continue
ADD W I 1, R0
SH I -1, 64+!R13, 64+!R13
JUMP while

continue:
MOVE W R0, 68+!R13

MOVE W R13, SP
POPR
RET

convertToIEEE754:
PUSHR
MOVE W SP, R13
CLEAR W R0
CLEAR W R1
CLEAR W R2
CLEAR W R3
CLEAR W R4
CLEAR W R5

CLEAR W  -!SP
MOVE W 64+!R13, -!SP
CALL count
ADD W I 4, SP
MOVE W !SP+, R0

MOVE W R0, R2
ADD W I 127, R0

CMP W 64+!R13, 0
JGT zero
ADD W I 1, R1

zero:
CLEAR W  -!SP
MOVE W R0, -!SP
CALL count
ADD W I 4, SP
MOVE W !SP+, R3
ADD W I 1, R3
SUB W R3, I 31, R3

SH I 32, R1, R1
SH R3, R0, R0

ADD W I 1, R4
SUB W R2, I 23, R4
ADD W I 1, R5
SH R2, R5, R5
XOR W R5, 64+!R13, 64+!R13
SH R4, 64+!R13, R4

ADD W R0, R1, R1
ADD W R1, R4, 68+!R13

MOVE W R13, SP
POPR
RET
'''

    def arrayIndexLocation(self):
        return '''
arrayLocation:
PUSHR
MOVE W SP, R13
CLEAR W R0
MOVE W 64+!R13, R1
MOVE W 68+!R13, R2
MOVE W !R1+, R3
loop:
MOVE W !R2+, R4
CMP W !R1, R4
JLE error
MULT W !R1+, R0	
ADD W R4, R0
SUB W I 1, R3
JGT loop
endloop:
MULT W !R1+, R0
ADD W !R1+, R0
MOVE W R0, 72+!R13
MOVE W R13, SP
POPR
RET
error:
HALT
'''
