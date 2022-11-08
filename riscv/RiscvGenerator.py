from shared.Generator import Generator
from shared.struct import StructDefinitions
from shared.variables import TypeCheck
from shared.variables.Variable import Variable
from shared.allocation.DataAllocator import *
from shared.SymbolGenerator import createNewSymbol


class RiscvGenerator(Generator):
    def __init__(self, goals, scope):
        self.generated_code = []
        super().__init__(goals, scope)

    def generateStructCreate(self, struct):
        self.generated_code.append('mv t0, t6')

        offset = 0
        for definition in StructDefinitions.findDefinition(struct.name):
            offset += StructDefinitions.getOffsetForType(definition.type_def)

        self.generated_code.append('addi t6, t6, ' + str(offset))
        self.generated_code.append('addi sp, sp, -4')
        self.generated_code.append('sw t6, 0(sp)')

    def generateStructAssignment(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        TypeCheck.checkTypeForVariable(type_def, struct.value, scope)
        self.generate(struct.value, scope)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('l' + lop + ' t0, 0(sp)')
                self.generated_code.append('s' + lop + ' t0, ' + attr_offset + '(s' + str(variable.offset - 1) + ')')
            case Location.STACK:
                self.generated_code.append('l' + lop + ' t0, 0(sp)')
                self.generated_code.append('l' + lop + ' t1, -' + str(variable.offset * 4) + '(fp)')
                self.generated_code.append('s' + lop + ' t0, ' + attr_offset + '(t1)')

    def generateStructResolve(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        lop = self.getSpaceForType(type_def)
        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('l' + lop + ' t0, ' + attr_offset + '(s' + str(variable.offset - 1) + ')')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append('s' + lop + ' t0, 0(sp)')
            case Location.STACK:
                self.generated_code.append('l' + lop + ' (-' + str(variable.offset * 4) + '(fp), t0')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append('s' + lop + ' ' + attr_offset + '(t0), (sp)')

    def generateLoopStatement(self, while_statement, scope):
        local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
        while_symbol = createNewSymbol('while')
        continue_symbol = createNewSymbol('continue')

        self.generated_code.append('')  # formatting
        self.generated_code.append(while_symbol + ':')
        self.generate(while_statement.condition, local_scope)

        self.generated_code.append('lw t0, 0(sp)')
        self.generated_code.append('addi t1, zero, 1')  # for comparing if statement
        self.generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack
        self.generated_code.append('bne t0, t1, ' + continue_symbol)

        for statement in while_statement.statements:
            self.generate(statement, local_scope)

        self.generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer
        self.generated_code.append('j ' + while_symbol)

        self.generated_code.append('')  # formatting
        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer

    def generateIfStatement(self, if_statement, scope):
        local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
        else_symbol = createNewSymbol('else')
        continue_symbol = createNewSymbol('continue')

        has_else = len(if_statement.else_statements) != 0

        self.generate(if_statement.condition, scope)
        self.generated_code.append('lw t0, 0(sp)')
        self.generated_code.append('addi t1, zero, 1')  # for comparing if statement
        self.generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack
        self.generated_code.append('bne t0, t1, ' + (else_symbol if has_else else continue_symbol))

        self.generated_code.append('')  # formatting
        for statement in if_statement.statements:
            self.generate(statement, local_scope)

        if has_else:
            self.generated_code.append('j ' + continue_symbol)
            self.generated_code.append(else_symbol + ': ')
            for statement in if_statement.else_statements:
                self.generate(statement, local_scope)

        self.generated_code.append('')  # formatting
        self.generated_code.append(continue_symbol + ":")
        self.generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer

    def generateVariableCreation(self, variable_creation, scope):
        name = variable_creation.name
        type_def = variable_creation.type_def

        TypeCheck.checkTypeForVariable(type_def, variable_creation.value, scope)

        self.generate(variable_creation.value, scope)
        variable = scope.addData(Variable(name, type_def))

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
                self.generated_code.append('addi sp, sp, 4')  # reset stack pointer
            case Location.STACK:
                self.generated_code.append('sw t0, 0(sp)')

    def generateVariableAssignment(self, variable_assignment, scope):
        name = variable_assignment.name
        self.generate(variable_assignment.value, scope)
        variable = scope.findData(name)
        type_def = variable.data.type_def

        TypeCheck.checkTypeForVariable(type_def, variable_assignment.value, scope)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
                self.generated_code.append('addi sp, sp, 4')  # reset stack pointer
            case Location.STACK:
                self.generated_code.append('s' + self.getSpaceForType(type_def) + ' t0, -' + str(variable.offset * 4) + '(fp)')

    def generateResolveVariable(self, variable, scope):
        variable = scope.findData(variable.name)
        type_def = variable.data.type_def

        self.generated_code.append('addi sp, sp, -4')
        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('s' + self.getSpaceForType(type_def) + ' s' + str(variable.offset - 1) + ', 0(sp)')
                self.generated_code.append('l' + self.getSpaceForType(type_def) + ' t0, 0(sp)')
            case Location.STACK:
                self.generated_code.append('l' + self.getSpaceForType(type_def) + ' t0, -' + str(variable.offset * 4) + '(fp)')
                self.generated_code.append('s' + self.getSpaceForType(type_def) + ' t0, 0(sp)')
                self.generated_code.append('l' + self.getSpaceForType(type_def) + ' t0, 0(sp)')

    def generateBinaryOp(self, binary_op, scope):
        self.generate(binary_op.left, scope)
        self.generate(binary_op.right, scope)

        op = binary_op.op
        match op:
            case '+':
                self.generateArithmetic(op)
            case '-':
                self.generateArithmetic(op)
            case '*':
                self.generateArithmetic(op)
            case '/':
                self.generateArithmetic(op)
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
                self.generated_code.append('lw t0, 4(sp)')
                self.generated_code.append('lw t1, 0(sp)')

                self.generated_code.append('or t0, t0, t1')
                self.generated_code.append('addi sp, sp, 8')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append('sw t0, 0(sp)')
            case 'and':
                self.generated_code.append('lw t0, 4(sp)')
                self.generated_code.append('lw t1, 0(sp)')

                self.generated_code.append('and t0, t0, t1')
                self.generated_code.append('addi sp, sp, 8')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append('sw t0, 0(sp)')

    def generateArithmetic(self, op):
        mappings = {"+": "add",
                    "-": "sub",
                    "/": "div",
                    "*": "mul"}

        self.generated_code.append('lw t0, 4(sp)')
        self.generated_code.append('lw t1, 0(sp)')

        self.generated_code.append(mappings.get(op) + ' t0, t0, t1')
        self.generated_code.append('addi sp, sp, 8')
        self.generated_code.append('addi sp, sp, -4')
        self.generated_code.append('sw t0, 0(sp)')

    def generateComparison(self, op):
        mappings = {">": "BGT",
                    ">=": "BGE",
                    "==": "BEQ",
                    "<=": "BLE",
                    "<": "BLT"}
        symbol = createNewSymbol('logicalTrue')
        symbol_continue = createNewSymbol('continue')

        self.generated_code.append('lw t0, 4(sp)')
        self.generated_code.append('lw t1, 0(sp)')
        self.generated_code.append('addi sp, sp, 8')
        self.generated_code.append('addi sp, sp, -4')
        self.generated_code.append(mappings.get(op) + ' t0, t1, ' + symbol)
        self.generated_code.append('add t0, zero, zero')
        self.generated_code.append('sb t0, 0(sp)')
        self.generated_code.append('j ' + symbol_continue)
        self.generated_code.append('')
        self.generated_code.append(symbol + ':')
        self.generated_code.append('addi t0, zero, 1')
        self.generated_code.append('sb t0, 0(sp)')
        self.generated_code.append('')
        self.generated_code.append(symbol_continue + ':')

    def generateConstant(self, constant):
        if constant.value == 'true':
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append('addi t0, zero, 1')
            self.generated_code.append('sw t0, 0(sp)')
        elif constant.value == 'false':
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append('addi t0, zero, 0')
            self.generated_code.append('sw t0, 0(sp)')
        else:
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append('addi t0, zero, ' + str(constant.value))
            self.generated_code.append('sw t0, 0(sp)')

    def generateInit(self):
        return '''
    .section .text
    .global __start
    
    __start:
    mv fp, sp
    mv t6, gp     
    '''

    def generateHeap(self):
        return ''

    def getSpaceForType(self, type_def):
        match type_def:
            case 'int':
                return 'w'
            case 'boolean':
                return 'b'
            case _:
                return 'w'
