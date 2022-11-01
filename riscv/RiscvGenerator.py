from shared.struct import StructDefinitions
from shared.variables import TypeCheck
from shared.variables.Variable import Variable
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.statement.ForStatement import ForStatement
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from shared.allocation.DataAllocator import *
from shared.SymbolGenerator import createNewSymbol
from syntaxTree.statement.WhileStatement import WhileStatement
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve

generated_code = []


def generateMachineCode(goals, scope):
    generated_code.append(generateInit())
    for goal in goals:
        generate(goal, scope)
    return generated_code


def generate(ast, scope):
    if type(ast) is StructNode:
        generateStruct(ast)
    if type(ast) is StructCreate:
        generateStructCreate(ast)
    if type(ast) is StructAssignment:
        generateStructAssignment(ast, scope)
    if type(ast) is StructResolve:
        generateStructResolve(ast, scope)
    if type(ast) is ForStatement:
        generateForStatement(ast, scope)
    if type(ast) is WhileStatement:
        generateWhileStatement(ast, scope)
    if type(ast) is IfStatement:
        generateIfStatement(ast, scope)
    if type(ast) is VariableCreation:
        generateVariableCreation(ast, scope)
    if type(ast) is VariableAssignment:
        generateVariableAssignment(ast, scope)
    elif type(ast) is BinaryOp:
        generateBinaryOp(ast, scope)
    elif type(ast) is Constant:
        generateConstant(ast)
    elif type(ast) is VariableNode:
        generateResolveVariable(ast, scope)


def generateStruct(struct):
    StructDefinitions.addDefinition(struct)


def generateStructCreate(struct):
    generated_code.append('mv t0, t6')

    offset = 0
    for definition in StructDefinitions.findDefinition(struct.name):
        match definition.type_def:
            case 'int':
                offset += 4
            case 'boolean':
                offset += 1

    generated_code.append('addi t6, t6, ' + str(offset))
    generated_code.append('addi sp, sp, -4')
    generated_code.append('sw t6, 0(sp)')


def generateStructAssignment(struct, scope):
    variable = scope.findData(struct.name)
    struct_name = variable.data.type_def
    struct_attribute = struct.attribute
    type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

    TypeCheck.checkType(type_def, struct.value, scope)
    generate(struct.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, 0(sp)')
            generated_code.append('s' + getSpaceForType(type_def) + ' t0, ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + '(s' + str(variable.offset - 1) + ')')
        case Location.STACK:
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, 0(sp)')
            generated_code.append('l' + getSpaceForType(type_def) + ' t1, -' + str(variable.offset * 4) + '(fp)')
            generated_code.append('s' + getSpaceForType(type_def) + ' t0, ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + '(t1)')


def generateStructResolve(struct, scope):
    variable = scope.findData(struct.name)
    struct_name = variable.data.type_def
    struct_attribute = struct.attribute
    type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + '(s' + str(variable.offset - 1) + ')')
            generated_code.append('addi sp, sp, -4')
            generated_code.append('s' + getSpaceForType(type_def) + ' t0, 0(sp)')
        case Location.STACK:
            generated_code.append('l' + getSpaceForType(type_def) + ' (-' + str(variable.offset * 4) + '(fp), t0')
            generated_code.append('addi sp, sp, -4')
            generated_code.append('s' + getSpaceForType(type_def) + ' ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + '(t0), (sp)')


def generateForStatement(for_statement, scope):
    index_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    for_symbol = createNewSymbol('for')
    continue_symbol = createNewSymbol('continue')

    # init index variable
    generate(VariableCreation(for_statement.index_var_name, 'int', for_statement.range_from), index_scope)
    generate(VariableCreation('!', 'int', for_statement.range_to), index_scope)

    generated_code.append('')   # formatting
    generated_code.append(for_symbol + ':')
    generate(
        BinaryOp(
            VariableNode(for_statement.index_var_name),
            '<=',
            VariableNode('!')
        ), index_scope)

    for_scope = DataAllocator(index_scope, index_scope.dataInRegister, index_scope.dataInStack)
    generated_code.append('lw t0, 0(sp)')
    generated_code.append('addi t1, zero, 1')  # for comparing if statement
    generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack
    generated_code.append('bne t0, t1, ' + continue_symbol)

    for statement in for_statement.statements:
        generate(statement, for_scope)

    generate(VariableAssignment(for_statement.index_var_name, BinaryOp(VariableNode(for_statement.index_var_name), '+', Constant(1))), for_scope)
    generated_code.append('addi sp, sp, ' + str(for_scope.getDataInStack() * 4))  # reset Stack Pointer
    generated_code.append('j ' + for_symbol)

    generated_code.append('addi sp, sp, ' + str(for_scope.getDataInStack() * 4))  # reset Stack Pointer
    generated_code.append('')  # formatting
    generated_code.append(continue_symbol + ":")
    generated_code.append('addi sp, sp, ' + str(index_scope.getDataInStack() * 4))  # reset Stack Pointer


def generateWhileStatement(while_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    while_symbol = createNewSymbol('while')
    continue_symbol = createNewSymbol('continue')

    generated_code.append('')           # formatting
    generated_code.append(while_symbol + ':')
    generate(while_statement.condition, local_scope)

    generated_code.append('lw t0, 0(sp)')
    generated_code.append('addi t1, zero, 1')  # for comparing if statement
    generated_code.append('addi sp, sp, 4')  # reset Stack Pointer from logical calculation in Stack
    generated_code.append('bne t0, t1, ' + continue_symbol)

    for statement in while_statement.statements:
        generate(statement, local_scope)

    generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer
    generated_code.append('j ' + while_symbol)

    generated_code.append('')   # formatting
    generated_code.append(continue_symbol + ":")
    generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer


def generateIfStatement(if_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    else_symbol = createNewSymbol('else')
    continue_symbol = createNewSymbol('continue')

    has_else = len(if_statement.else_statements) != 0

    generate(if_statement.condition, scope)
    generated_code.append('lw t0, 0(sp)')
    generated_code.append('addi t1, zero, 1')    # for comparing if statement
    generated_code.append('addi sp, sp, 4')      # reset Stack Pointer from logical calculation in Stack
    generated_code.append('bne t0, t1, ' + (else_symbol if has_else else continue_symbol))

    generated_code.append('')   # formatting
    for statement in if_statement.statements:
        generate(statement, local_scope)

    if has_else:
        generated_code.append('j ' + continue_symbol)
        generated_code.append(else_symbol + ': ')
        for statement in if_statement.else_statements:
            generate(statement, local_scope)

    generated_code.append('')   # formatting
    generated_code.append(continue_symbol + ":")
    generated_code.append('addi sp, sp, ' + str(local_scope.getDataInStack() * 4))  # reset Stack Pointer


def generateVariableCreation(variable_creation, scope):
    name = variable_creation.name
    type_def = variable_creation.type_def

    TypeCheck.checkType(type_def, variable_creation.value, scope)

    generate(variable_creation.value, scope)
    variable = scope.addData(Variable(name, type_def))

    match variable.location:
        case Location.REGISTER:
            generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
            generated_code.append('addi sp, sp, 4')         # reset stack pointer
        case Location.STACK:
            generated_code.append('sw t0, 0(sp)')


def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findData(name)
    type_def = variable.data.type_def

    TypeCheck.checkType(type_def, variable_assignment.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
            generated_code.append('addi sp, sp, 4')  # reset stack pointer
        case Location.STACK:
            generated_code.append('s' + getSpaceForType(type_def) + ' t0, -' + str(variable.offset * 4) + '(fp)')


def generateResolveVariable(variable, scope):
    variable = scope.findData(variable.name)
    type_def = variable.data.type_def

    generated_code.append('addi sp, sp, -4')
    match variable.location:
        case Location.REGISTER:
            generated_code.append('s' + getSpaceForType(type_def) + ' s' + str(variable.offset - 1) + ', 0(sp)')
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, 0(sp)')
        case Location.STACK:
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, -' + str(variable.offset * 4) + '(fp)')
            generated_code.append('s' + getSpaceForType(type_def) + ' t0, 0(sp)')
            generated_code.append('l' + getSpaceForType(type_def) + ' t0, 0(sp)')


def generateBinaryOp(binary_op, scope):
    generate(binary_op.left, scope)
    generate(binary_op.right, scope)

    op = binary_op.op
    match op:
        case '+':
            generateArithmetic(op)
        case '-':
            generateArithmetic(op)
        case '*':
            generateArithmetic(op)
        case '/':
            generateArithmetic(op)
        case '>':
            generateComparison('>')
        case '>=':
            generateComparison('>=')
        case '==':
            generateComparison('==')
        case '<=':
            generateComparison('<=')
        case '<':
            generateComparison('<')
        case 'or':
            generated_code.append('lw t0, 4(sp)')
            generated_code.append('lw t1, 0(sp)')

            generated_code.append('or t0, t0, t1')
            generated_code.append('addi sp, sp, 8')
            generated_code.append('addi sp, sp, -4')
            generated_code.append('sw t0, 0(sp)')
        case 'and':
            generated_code.append('lw t0, 4(sp)')
            generated_code.append('lw t1, 0(sp)')

            generated_code.append('and t0, t0, t1')
            generated_code.append('addi sp, sp, 8')
            generated_code.append('addi sp, sp, -4')
            generated_code.append('sw t0, 0(sp)')


def generateArithmetic(op):
    mappings = {"+": "add",
                "-": "sub",
                "/": "div",
                "*": "mul"}

    generated_code.append('lw t0, 4(sp)')
    generated_code.append('lw t1, 0(sp)')

    generated_code.append(mappings.get(op) + ' t0, t0, t1')
    generated_code.append('addi sp, sp, 8')
    generated_code.append('addi sp, sp, -4')
    generated_code.append('sw t0, 0(sp)')


def generateComparison(op):
    mappings = {">": "BGT",
                ">=": "BGE",
                "==": "BEQ",
                "<=": "BLE",
                "<": "BLT"}
    symbol = createNewSymbol('logicalTrue')
    symbol_continue = createNewSymbol('continue')

    generated_code.append('lw t0, 4(sp)')
    generated_code.append('lw t1, 0(sp)')
    generated_code.append('addi sp, sp, 8')
    generated_code.append('addi sp, sp, -4')
    generated_code.append(mappings.get(op) + ' t0, t1, ' + symbol)
    generated_code.append('add t0, zero, zero')
    generated_code.append('sw t0, 0(sp)')
    generated_code.append('j ' + symbol_continue)
    generated_code.append('')
    generated_code.append(symbol + ':')
    generated_code.append('addi t0, zero, 1')
    generated_code.append('sw t0, 0(sp)')
    generated_code.append('')
    generated_code.append(symbol_continue + ':')


def generateConstant(constant):
    if constant.value == 'true':
        generated_code.append('addi sp, sp, -4')
        generated_code.append('addi t0, zero, 1')
        generated_code.append('sw t0, 0(sp)')
    elif constant.value == 'false':
        generated_code.append('addi sp, sp, -4')
        generated_code.append('addi t0, zero, 0')
        generated_code.append('sw t0, 0(sp)')
    else:
        generated_code.append('addi sp, sp, -4')
        generated_code.append('addi t0, zero, ' + str(constant.value))
        generated_code.append('sw t0, 0(sp)')


def generateInit():
    return '''
.section .text
.global __start

__start:
mv fp, sp
mv t6, gp     
'''

def getSpaceForType(type_def):
    match type_def:
        case 'int':
            return 'w'
        case 'boolean':
            return 'b'
        case _:
            return 'w'