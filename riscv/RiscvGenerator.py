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

generated_code = []


def generateMachineCode(goals, scope):
    generated_code.append(generateInit())
    for goal in goals:
        generate(goal, scope)
    return generated_code


def generate(ast, scope):
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


def generateForStatement(for_statement, scope):
    index_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    for_symbol = createNewSymbol('for')
    continue_symbol = createNewSymbol('continue')

    # init index variable
    generate(VariableCreation(for_statement.index_var_name, for_statement.range_from), index_scope)
    generate(VariableCreation('!', for_statement.range_to), index_scope)

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
    generate(variable_creation.value, scope)
    variable = scope.addData(name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
            generated_code.append('addi sp, sp, 4')         # reset stack pointer
        case Location.STACK:
            generated_code.append('sw t0, 0(sp)')


def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findDataLocation(name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('add  s' + str(variable.offset - 1) + ', t0, zero')
            generated_code.append('addi sp, sp, 4')  # reset stack pointer
        case Location.STACK:
            generated_code.append('sw t0, -' + str(variable.offset * 4) + '(gp)')


def generateResolveVariable(variable, scope):
    variable = scope.findDataLocation(variable.name)

    generated_code.append('addi sp, sp, -4')
    match variable.location:
        case Location.REGISTER:
            generated_code.append('sw s' + str(variable.offset - 1) + ', 0(sp)')
            generated_code.append('lw t0, 0(sp)')
        case Location.STACK:
            generated_code.append('lw t0, -' + str(variable.offset * 4) + '(gp)')
            generated_code.append('sw t0, 0(sp)')
            generated_code.append('lw t0, 0(sp)')


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
    generated_code.append('addi sp, sp, -4')
    generated_code.append('addi t0, zero, ' + str(constant.value))
    generated_code.append('sw t0, 0(sp)')


def generateInit():
    return '''
.section .text
.global __start

__start:
mv sp, gp     
'''
