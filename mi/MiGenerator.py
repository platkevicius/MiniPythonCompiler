from shared.Generator import Generator
from shared.struct import StructDefinitions
from shared.variables import TypeCheck
from shared.variables.Variable import Variable
from shared.allocation.DataAllocator import *
from shared.SymbolGenerator import createNewSymbol


class MiGenerator(Generator):
    def __init__(self, goals, scope):
        self.generated_code = []
        super().__init__(goals, scope)

    def generateMachineCode(self):
        self.generated_code.append(self.generateInit())
        for goal in self.goals:
            self.generate(goal, self.scope)
        self.generated_code.append('HALT')
        self.generated_code.append(self.generateHeap())
        return self.generated_code

    def generateStructCreate(self, struct):
        self.generated_code.append('MOVE W hp, R13')

        offset = 0
        for definition in StructDefinitions.findDefinition(struct.name):
            offset += StructDefinitions.getOffsetForType(definition.type_def)

        self.generated_code.append('ADD W I ' + str(offset) + ', hp')
        self.generated_code.append('MOVE W R13, -!SP')

    def generateStructAssignment(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        TypeCheck.checkType(type_def, struct.value, scope)
        self.generate(struct.value, scope)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        variable_offset = str(variable.offset)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('MOVE ' + lop + ' !SP+, ' + attr_offset + ' +!R' + variable_offset)
            case Location.STACK:
                self.generated_code.append('MOVE ' + lop + ' !SP+, ' + attr_offset + ' !(-' + str(variable.offset * 4) + '+!R12)')

    def generateStructResolve(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        variable_offset = str(variable.offset)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('MOVE ' + lop + ' ' + attr_offset + '+!R' + variable_offset + ', -!SP')
            case Location.STACK:
                self.generated_code.append('MOVE ' + lop + ' ' + attr_offset + ' !(-' + str(variable.offset * 4) + '+!R12), -!SP')

    def generateLoopStatement(self, while_statement, scope):
        local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
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

        self.generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer
        self.generated_code.append('JUMP ' + while_symbol)

        self.generated_code.append('')  # formatting
        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer

    def generateIfStatement(self, if_statement, scope):
        local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
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
            self.generated_code.append('JUMP ' + continue_symbol)
            self.generated_code.append(else_symbol + ': ')
            for statement in if_statement.else_statements:
                self.generate(statement, local_scope)

        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer

    def generateVariableCreation(self, variable_creation, scope):
        name = variable_creation.name
        type_def = variable_creation.type_def
        self.generate(variable_creation.value, scope)
        variable = scope.addData(Variable(name, type_def))

        TypeCheck.checkType(type_def, variable_creation.value, scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('MOVE ' + self.getSpaceForType(type_def) + ' !SP, R' + str(variable.offset))
            case Location.STACK:
                self.generated_code.append('SUB W I 4, SP')

        self.generated_code.append('ADD W I 4, SP')  # reset stack pointer

    def generateVariableAssignment(self, variable_assignment, scope):
        name = variable_assignment.name
        self.generate(variable_assignment.value, scope)
        variable = scope.findData(name)
        type_def = variable.data.type_def

        TypeCheck.checkType(variable.data.type_def, variable_assignment.value, scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('MOVE ' + self.getSpaceForType(type_def) + ' !SP, R' + str(variable.offset))
            case Location.STACK:
                self.generated_code.append(
                    'MOVE ' + self.getSpaceForType(type_def) + ' !SP, -' + str(variable.offset * 4) + '+!R12')

        self.generated_code.append('ADD W I 4, SP')

    def generateResolveVariable(self, variable, scope):
        variable = scope.findData(variable.name)
        type_def = variable.data.type_def

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('MOVE ' + self.getSpaceForType(type_def) + ' R' + str(variable.offset)
                                           + ', -!SP')
            case Location.STACK:
                self.generated_code.append(
                    'MOVE ' + self.getSpaceForType(type_def) + ' -' + str(variable.offset * 4) + '+!R12, -!SP')

    def generateBinaryOp(self, binary_op, scope):
        self.generate(binary_op.left, scope)
        self.generate(binary_op.right, scope)

        op = binary_op.op
        match op:
            case '+':
                self.generated_code.append('ADD W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')
            case '-':
                self.generated_code.append('SUB W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')
            case '*':
                self.generated_code.append('MULT W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')
            case '/':
                self.generated_code.append('DIV W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')
            case '>':
                self.generateComparison('>')
            case '>=':
                self.generateComparison('>=')
            case '==':
                self.generateComparison('==')
            case '<=':
                self.generateComparison('<=')
            case '<':
                self.generateComparison('<')
            case 'or':
                self.generated_code.append('OR W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')
            case 'and':
                self.generated_code.append('MULT W !SP, 4+!SP')
                self.generated_code.append('ADD W I 4, SP')

    def generateComparison(self, op):
        mappings = {">": "JGT",
                    ">=": "JGE",
                    "==": "JEQ",
                    "<=": "JLE",
                    "<": "JLE"}
        symbol = createNewSymbol('logicalTrue')
        symbol_continue = createNewSymbol('continue')

        self.generated_code.append('SUB W !SP, 4+!SP')
        self.generated_code.append('ADD W I 4, SP')
        self.generated_code.append('CMP W !SP, I 0')
        self.generated_code.append(mappings.get(op) + ' ' + symbol)
        self.generated_code.append('MOVE B I 0, !SP')
        self.generated_code.append('JUMP ' + symbol_continue)
        self.generated_code.append('')
        self.generated_code.append(symbol + ':')
        self.generated_code.append('MOVE B I 1, !SP')
        self.generated_code.append('')
        self.generated_code.append(symbol_continue + ':')

    def generateConstant(self, constant):
        if constant.value == 'true':
            self.generated_code.append('MOVE B I 1, -!SP')
        elif constant.value == 'false':
            self.generated_code.append('MOVE B I 0, -!SP')
        else:
            self.generated_code.append('MOVE W I ' + str(constant.value) + ', -!SP')

    def generateInit(self):
        return '''
    SEG
    MOVE W I H'10000', SP
    MOVE W I H'10000', R12
    MOVEA heap, hp
    
    start:'''

    def generateHeap(self):
        return '''
    hp: RES 4
    heap: RES 0'''

    def getSpaceForType(self, type_def):
        match type_def:
            case 'int':
                return 'W'
            case 'boolean':
                return 'B'
            case 'float':
                return 'F'
            case _:
                return 'W'
