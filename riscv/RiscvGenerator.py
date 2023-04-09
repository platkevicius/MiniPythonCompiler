import struct

from riscv.RiscvAllocator import RiscvAllocator
from riscv.FunctionEnvironment import FunctionEnvironment
from shared.Generator import Generator
from shared.allocation.Location import Location
from shared.function import FunctionDefinitions
from shared.function.Function import Function
from shared.struct import StructDefinitions
from shared.type import TypeResolver
from shared.variables.Variable import Variable
from shared.SymbolGenerator import createNewSymbol
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.function.FunctionCreate import FunctionCreate
from syntaxTree.struct.StructNode import StructNode


class RiscvGenerator(Generator):
    def __init__(self, goals, scope):
        self.generated_code = []
        self.data_section = []
        super().__init__(goals, scope)

    def generateMachineCode(self):
        definitions = []
        for goal in self.goals:
            if type(goal) is FunctionCreate or type(goal) is StructNode:
                definitions.append(goal)

        self.generated_code.append(self.generateInit())

        self.generated_code.append('j start')

        self.generated_code.append(self.arrayIndexLocation())

        for definition in definitions:
            self.generate(definition, self.scope)

        self.generated_code.append('start:')
        self.goals = [x for x in self.goals if x not in definitions]
        for goal in self.goals:
            self.generate(goal, self.scope)

        if len(self.data_section) != 0:
            self.generated_code.append('.data:')

        for data in self.data_section:
            self.generated_code.append(data)

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

        body_scope = RiscvAllocator(param_scope, param_scope.dataInRegister, 0, 0)
        self.generated_code.append(name + ': ')
        self.pushr(body_scope)
        self.generated_code.append('mv s11, sp')
        for statement in ast.statements:
            self.generate(statement, body_scope)

    def generateFunctionCall(self, ast, scope):
        function = FunctionDefinitions.findDefinition(ast.name)

        if len(function.params) != len(ast.params):
            raise ValueError('param size is not equivalent')

        if scope.isInFunction():
            # save frame pointer
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append('sw s11, 0(sp)')

            # save return address
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append('sw ra, 0(sp)')

            # save arguments
            param_offset = scope.getNonFloatParams()
            for i in reversed(range(0, param_offset - 1)):
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append(f'sw a{i}, 0(sp)')

            param_offset = scope.getFloatParams()
            for i in reversed(range(0, param_offset - 1)):
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append(f'fsw fa{i}, 0(sp)')

        # remove parameter from stack
        for i in range(0, len(function.params)):
            expr = ast.params[i]
            self.generate(expr, scope)

        floatCount = FunctionDefinitions.countFloatParams(ast.name)-1
        intCount = FunctionDefinitions.countNonFloatParams(ast.name)-1
        for i in reversed(range(0, len(function.params))):
            prefix = ''
            index = intCount
            if function.params[i].type_def == 'float':
                prefix = 'f'
                index = floatCount
                floatCount -= 1
            else:
                intCount -= 1

            self.generated_code.append(f'{prefix}lw {prefix}a{index}, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')

        self.generated_code.append(f'jal {function.name}')

        if function.return_type == 'float':
            self.generated_code.append('fmv.w.x ft0, zero')
            self.generated_code.append('fadd.s ft0, ft0, fa0')
        else:
            self.generated_code.append('mv t0, a0')

        if scope.isInFunction():
            # retrieve arguments
            param_offset = scope.getFloatParams()
            for i in range(0, param_offset - 1):
                self.generated_code.append(f'flw fa{i}, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')

            param_offset = scope.getNonFloatParams()
            for i in range(0, param_offset - 1):
                self.generated_code.append(f'lw a{i}, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')

            # retrieve return address
            self.generated_code.append('lw ra, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')

            # retrieve frame pointer
            self.generated_code.append('lw s11, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')

        self.generated_code.append('addi sp, sp, -4')
        if function.return_type == 'float':
            self.generated_code.append(f'fsw ft0, 0(sp)')
        else:
            self.generated_code.append(f'sw t0, 0(sp)')

    def generateReturnStatement(self, ast, scope):
        return_data = scope.findData('return')
        type_def = return_data.data.type_def
        prefix = ''
        if type_def == 'float':
            prefix = 'f'

        self.generate(ast.expression, scope)

        self.generated_code.append(f'{prefix}lw {prefix}a0, 0(sp)')
        self.generated_code.append('addi sp, sp, 4')
        self.generated_code.append('mv sp, s11')  # reset Stack Pointer
        self.popr(scope)
        self.generated_code.append('jr ra')

    def generateStructCreate(self, struct):
        self.generated_code.append('mv t0, gp')

        offset = 0
        for definition in StructDefinitions.findDefinition(struct.name):
            offset += StructDefinitions.getOffsetForType(definition.type_def)

        self.generated_code.append(f'addi gp, gp, {offset}')
        self.generated_code.append('addi sp, sp, -4')
        self.generated_code.append('sw gp, 0(sp)')

    def generateStructAssignment(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute

        self.generate(struct.value, scope)

        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        prefix = ''
        if type_def == 'float':
            prefix = 'f'

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'{prefix}lw {prefix}t0, 0(sp)')
                self.generated_code.append(f'{prefix}sw {prefix}t0, {attr_offset}(s{variable.offset})')
            case Location.STACK:
                relative = self.getRelativeRegister(scope, Location.STACK)
                self.generated_code.append(f'{prefix}lw {prefix}t0, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')
                self.generated_code.append(f'lw t1, {variable.offset * 4}({relative})')
                self.generated_code.append(f'{prefix}sw {prefix}t0, {attr_offset}(t1)')

    def generateStructResolve(self, struct, scope):
        variable = scope.findData(struct.name)
        struct_name = variable.data.type_def
        struct_attribute = struct.attribute

        attr_offset = str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute))
        type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

        prefix = ''
        if type_def == 'float':
            prefix = 'f'

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'{prefix}lw {prefix}t0, {attr_offset}(s{variable.offset})')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')
            case Location.STACK:
                relative = self.getRelativeRegister(scope, Location.STACK)
                self.generated_code.append(f'{prefix}lw {prefix}t0, {variable.offset * 4}({relative})')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append(f'{prefix}lw {prefix}t0, {attr_offset}(t0)')
                self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')

    def generateLoopStatement(self, while_statement, scope):
        local_scope = RiscvAllocator(scope, scope.data_in_register_int, 0, scope.dataInStack)
        while_symbol = createNewSymbol('while')
        continue_symbol = createNewSymbol('continue')

        self.generated_code.append('')  # formatting
        self.generated_code.append(f'{while_symbol}:')
        self.generate(while_statement.condition, local_scope)

        self.generated_code.append('lw t0, 0(sp)')
        self.generated_code.append('addi t1, zero, 1')  # for comparing if statement
        self.generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack
        self.generated_code.append(f'bne t0, t1, {continue_symbol}')

        for statement in while_statement.statements:
            self.generate(statement, local_scope)

        local_variable_offset = local_scope.getOffsetForLocalVariable() * 4
        self.generated_code.append(f'addi sp, sp, {local_variable_offset}')  # reset Stack Pointer
        self.generated_code.append(f'j {while_symbol}')

        self.generated_code.append('')  # formatting
        self.generated_code.append(f'{continue_symbol}:')
        self.generated_code.append(f'addi sp, sp, {local_variable_offset}')  # reset Stack Pointer

    def generateIfStatement(self, if_statement, scope):
        local_scope = RiscvAllocator(scope, scope.data_in_register_int, 0, scope.dataInStack)
        else_symbol = createNewSymbol('else')
        continue_symbol = createNewSymbol('continue')

        has_else = len(if_statement.else_statements) != 0
        local_variable_offset = local_scope.getOffsetForLocalVariable() * 4

        self.generate(if_statement.condition, scope)
        self.generated_code.append('lw t0, 0(sp)')
        self.generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack

        self.generated_code.append('addi t1, zero, 1')  # for comparing if statement
        self.generated_code.append('bne t0, t1, ' + (else_symbol if has_else else continue_symbol))

        self.generated_code.append('')  # formatting
        for statement in if_statement.statements:
            self.generate(statement, local_scope)

        if has_else:
            self.generated_code.append(f'j {continue_symbol}')
            self.generated_code.append(f'{else_symbol}:')
            for statement in if_statement.else_statements:
                self.generate(statement, local_scope)

        self.generated_code.append('')  # formatting
        self.generated_code.append(f'{continue_symbol}:')
        self.generated_code.append(f'addi sp, sp, {local_variable_offset}')  # reset Stack Pointer

    def generateArrayCreate(self, ast, scope):
        self.generated_code.append('mv t5, gp')

        self.generated_code.append(f'addi gp, gp, {4 * (len(ast.dimensions) + 3)}')
        self.generated_code.append(f'addi t4, zero, {len(ast.dimensions)}')
        self.generated_code.append(f'sw t4, 0(t5)')
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
            self.generated_code.append(f'lw t4, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')
            self.generated_code.append(f'sw t4, {4 * counter}(t5)')
            counter += 1
        self.generated_code.append('addi t4, zero, 4')
        self.generated_code.append(f'sw t4, {4 * counter}(t5)')  # TODO: lop needs to be changed
        counter += 1
        self.generated_code.append('addi t4, gp, 4')
        self.generated_code.append(f'sw t4, {4 * counter}(t5)')  # basis address of array todo, change to use R13!
        for i in reversed(range(len(binOps) - 1, 0, -1)):
            op1 = binOps[i]
            op2 = binOps[i - 1]
            op2.right = op1
            binOps[i - 1] = op2

        self.generate(binOps[0], scope)
        self.generated_code.append(f'lw t4, 0(sp)')
        self.generated_code.append('addi sp, sp, 4')
        self.generated_code.append('add gp, gp, t4')
        self.generated_code.append('addi sp, sp, -4')
        self.generated_code.append('sw t5, 0(sp)')

    def generateArrayAssignment(self, ast, scope):
        self.generated_code.append('mv t5, gp')
        self.generated_code.append(f'addi gp, gp, {4 * (len(ast.index_expr))}')
        counter = 0
        for index in ast.index_expr:
            self.generate(ast.index_expr[index], scope)
            self.generated_code.append(f'lw t4, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')
            self.generated_code.append(f'sw t4, {4 * counter}(t5)')
            counter += 1

        variable = scope.findData(ast.name)
        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('mv a2, t5')
                self.generated_code.append(f'mv a1, s{variable.offset}')
                self.generated_code.append('jal arrayLocation')
                self.generate(ast.value_expr, scope)
                self.generated_code.append('lw t4, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')
                self.generated_code.append('sw t4, 0(a0)')
            case Location.STACK:
                relative_register = self.getRelativeRegister(scope, Location.STACK)
                self.generated_code.append('mv a2, t5')
                self.generated_code.append(f'lw a1, {variable.offset * 4}({relative_register})')
                self.generated_code.append('jal arrayLocation')
                self.generate(ast.value_expr, scope)
                self.generated_code.append('lw t4, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')
                self.generated_code.append('sw t4, 0(a0)')

    def generateArrayResolve(self, ast, scope):
        self.generated_code.append('mv t5, gp')
        self.generated_code.append(f'addi gp, gp, {4 * (len(ast.dimensions))}')
        counter = 0
        for index in ast.dimensions:
            self.generate(ast.dimensions[index], scope)
            self.generated_code.append(f'lw t4, 0(sp)')
            self.generated_code.append(f'sw t4, {4 * counter}(t5)')
            self.generated_code.append('addi sp, sp, 4')
            counter += 1

        variable = scope.findData(ast.name)
        match variable.location:
            case Location.REGISTER:
                self.generated_code.append('mv a2, t5')
                self.generated_code.append(f'mv a1, s{variable.offset}')
                self.generated_code.append('jal arrayLocation')
                self.generated_code.append('addi, sp, sp, -4')
                self.generated_code.append('lw t4, 0(a0)')
                self.generated_code.append('sw t4, 0(sp)')
            case Location.STACK:
                relative_register = self.getRelativeRegister(scope, Location.STACK)
                self.generated_code.append('mv a2, t5')
                self.generated_code.append(f'lw a1, {variable.offset * 4}({relative_register})')
                self.generated_code.append('jal arrayLocation')
                self.generated_code.append('addi, sp, sp, -4')
                self.generated_code.append('lw t4, 0(a0)')
                self.generated_code.append('sw t4, 0(sp)')

    def generateVariableCreation(self, variable_creation, scope):
        name = variable_creation.name
        type_def = variable_creation.type_def

        prefix = ""
        if type_def == 'float':
            prefix = "f"

        self.generate(variable_creation.value, scope)
        variable = scope.addData(Variable(name, type_def))

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'{prefix}lw {prefix}s{variable.offset}, 0(sp)')
                self.generated_code.append('addi sp, sp, 4')  # reset stack pointer

    def generateVariableAssignment(self, variable_assignment, scope):
        name = variable_assignment.name
        self.generate(variable_assignment.value, scope)
        variable = scope.findData(name)
        type_def = variable.data.type_def

        prefix = ""
        if type_def == 'float':
            prefix = "f"

        relative_register = self.getRelativeRegister(scope, Location.STACK)

        match variable.location:
            case Location.REGISTER:
                self.generated_code.append(f'{prefix}lw {prefix}s{variable.offset}, 0(sp)')
            case Location.STACK:
                self.generated_code.append(f'{prefix}sw {prefix}t0, {variable.offset * 4}({relative_register})')

        self.generated_code.append('addi sp, sp, 4')

    def generateResolveVariable(self, variable, scope):
        variable = scope.findData(variable.name)
        type_def = variable.data.type_def

        prefix = ""
        if type_def == 'float':
            prefix = "f"

        self.generated_code.append('addi sp, sp, -4')
        match variable.location:
            case Location.REGISTER:
                relative_register = self.getRelativeRegister(scope, Location.REGISTER)
                self.generated_code.append(f'{prefix}sw {prefix}{relative_register}{variable.offset}, 0(sp)')
            case Location.STACK:
                relative_register = self.getRelativeRegister(scope, Location.STACK)
                self.generated_code.append(f'{prefix}lw {prefix}t0, {variable.offset * 4}({relative_register})')
                self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')

    def generateBinaryOp(self, binary_op, scope):
        type_def = TypeResolver.resolveType(binary_op, scope)

        type_expr1 = TypeResolver.resolveType(binary_op.left, scope)
        type_expr2 = TypeResolver.resolveType(binary_op.right, scope)

        self.generate(binary_op.left, scope)

        if (type_expr1 == 'int' and type_def == 'float') or \
                (type_expr1 == 'int' and type_expr2 == 'float'):
            self.generated_code.append('lw t0, 0(sp)')
            self.generated_code.append('fcvt.s.w ft0, t0')
            self.generated_code.append('fsw ft0, 0(sp)')
            type_expr1 = 'float'

        self.generate(binary_op.right, scope)

        if (type_expr2 == 'int' and type_def == 'float') or \
                (type_expr2 == 'int' and type_def == 'float'):
            self.generated_code.append('lw t0, 0(sp)')
            self.generated_code.append('fcvt.s.w ft0, t0')
            self.generated_code.append('fsw ft0, 0(sp)')

        prefix = ""
        if type_def == 'float':
            prefix = "f"

        op = binary_op.op
        match op:
            case '+':
                self.generateArithmetic(op, type_def)
            case '-':
                self.generateArithmetic(op, type_def)
            case '*':
                self.generateArithmetic(op, type_def)
            case '/':
                self.generateArithmetic(op, type_def)
            case '>':
                self.generateComparison('>', type_expr1)
            case '>=':
                self.generateComparison('>=', type_expr1)
            case '==':
                self.generateComparison('==', type_expr1)
            case '<=':
                self.generateComparison('<=', type_expr1)
            case '<':
                self.generateComparison('<', type_expr1)
            case 'or':
                self.generated_code.append(f'{prefix}lw {prefix}t0, 4(sp)')
                self.generated_code.append(f'{prefix}lw {prefix}t1, 0(sp)')

                self.generated_code.append(f'or {prefix}t0, {prefix}t0, {prefix}t1')
                self.generated_code.append('addi sp, sp, 4')
                self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')
            case 'and':
                self.generated_code.append(f'{prefix}lw {prefix}t0, 4(sp)')
                self.generated_code.append(f'{prefix}lw {prefix}t1, 0(sp)')

                self.generated_code.append(f'and {prefix}t0, {prefix}t0, {prefix}t1')
                self.generated_code.append('addi sp, sp, 4')
                self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')

    def generateArithmetic(self, op, type_def):
        mappingsInt = {"+": "add",
                       "-": "sub",
                       "/": "div",
                       "*": "mul"}

        mappingFloat = {"+": "fadd.s",
                        "-": "fsub.s",
                        "/": "fdiv.s",
                        "*": "fmul.s"}

        prefix = ""
        if type_def == 'float':
            command = mappingFloat.get(op)
            prefix = "f"
        else:
            command = mappingsInt.get(op)

        self.generated_code.append(f'{prefix}lw {prefix}t0, 4(sp)')
        self.generated_code.append(f'{prefix}lw {prefix}t1, 0(sp)')

        self.generated_code.append(f'{command} {prefix}t0, {prefix}t0, {prefix}t1')
        self.generated_code.append('addi sp, sp, 4')
        self.generated_code.append(f'{prefix}sw {prefix}t0, 0(sp)')

    def generateComparison(self, op, type_def):
        mappingsInt = {">": "bgt",
                       ">=": "bge",
                       "==": "beq",
                       "<=": "ble",
                       "<": "blt"}
        mappingsFloat = {">": "flt.s",
                         ">=": "fle.s",
                         "==": "feq.s",
                         "<=": "fle.s",
                         "<": "flt.s"}

        prefix = ""
        if type_def == 'float':
            command = mappingsFloat.get(op)
            prefix = "f"
        else:
            command = mappingsInt.get(op)

        symbol = createNewSymbol('logicalTrue')
        symbol_continue = createNewSymbol('continue')

        if (op == '>' or op == '>=') and type_def == 'float':
            self.generated_code.append(f'{prefix}lw {prefix}t1, 4(sp)')
            self.generated_code.append(f'{prefix}lw {prefix}t0, 0(sp)')
        else:
            self.generated_code.append(f'{prefix}lw {prefix}t0, 4(sp)')
            self.generated_code.append(f'{prefix}lw {prefix}t1, 0(sp)')

        self.generated_code.append('addi sp, sp, 4')

        if type_def == 'int':
            self.generated_code.append(f'{command} {prefix}t0, {prefix}t1, {symbol}')
        else:
            self.generated_code.append(f'{command} t0, ft0, ft1')
            self.generated_code.append('li t1, 1')
            self.generated_code.append(f'beq t0, t1, {symbol}')

        self.generated_code.append('add t0, zero, zero')
        self.generated_code.append('sw t0, 0(sp)')
        self.generated_code.append(f'j {symbol_continue}')
        self.generated_code.append('')
        self.generated_code.append(f'{symbol}:')
        self.generated_code.append('addi t0, zero, 1')
        self.generated_code.append('sw t0, 0(sp)')
        self.generated_code.append('')
        self.generated_code.append(f'{symbol_continue}:')

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
            if type(constant.value) == int:
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append(f'addi t0, zero, {constant.value}')
                self.generated_code.append('sw t0, 0(sp)')
            else:
                symbol = createNewSymbol('float')
                self.data_section.append(f'{symbol}: .word {self.float_to_hex(constant.value)}')
                self.generated_code.append(f'lui t0, %hi({symbol})')
                self.generated_code.append(f'flw ft0, %lo({symbol})(t0)')
                self.generated_code.append('addi sp, sp, -4')
                self.generated_code.append('fsw ft0, 0(sp)')

    def generateInit(self):
        return '''
.text
.global __start
    
__start:
mv fp, sp
    '''

    def generateHeap(self):
        return ''

    def popr(self, scope):
        registerCount = scope.findUsedRegisters()

        for i in range(0, registerCount):
            self.generated_code.append(f'lw s{i}, 0(sp)')
            self.generated_code.append('addi sp, sp, 4')

    def pushr(self, scope):
        registerCount = scope.findUsedRegisters()

        for i in range(registerCount, 0, -1):
            self.generated_code.append('addi sp, sp, -4')
            self.generated_code.append(f'sw s{i}, 0(sp)')

    def getRelativeRegister(self, scope, location):
        if location is Location.REGISTER:
            match scope.isInFunction():
                case False:
                    return 's'
                case True:
                    return 'a'

        if location is Location.STACK:
            match scope.isInFunction():
                case False:
                    return 'fp'
                case True:
                    return 's11'

    def float_to_hex(self, num):
        bits, = struct.unpack('!I', struct.pack('!f', num))
        return hex(int("{:032b}".format(bits), 2))

    def arrayIndexLocation(self):
        return '''
arrayLocation:
mv t0, zero
mv t1, a1
mv t2, a2
lw t3, 0(t1)
addi t1, t1, 4
loop:
lw t4, 0(t2)
addi, t2, t2, 4
lw t5, 0(t1)
addi t1, t1, 4
ble t5, t4, error
mul t0, t0, t5
add t0, t0, t4
addi t3, t3, -1
blt zero, t3, loop
endloop:
lw t5, 0(t1)
addi t1, t1, 4
mul t0, t0, t5
lw t5, 0(t1)
addi t1, t1, 4
add t0, t0, t5
mv a0, t0
jr ra
error:
li a7, 10
ecall
'''