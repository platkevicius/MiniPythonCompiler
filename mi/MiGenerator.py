from mi.allocation.LocalScope import LocalScope
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from mi.allocation.DataAllocator import *
from mi.SymbolGenerator import createNewSymbol


def generateMachineCode(goals, scope):
    print(generateInit())
    for goal in goals:
        generate(goal, scope)
    print('HALT')
    print(generateHeap())


def generate(ast, scope):
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


def generateIfStatement(if_statement, scope):
    local_scope = LocalScope(scope)
    generate(if_statement.condition, local_scope)
    else_symbol = createNewSymbol('else')
    continue_symbol = createNewSymbol('continue')

    has_else = len(if_statement.else_statements) != 0

    print('CMP W I 1, !SP')
    print('JNE ' + (else_symbol if has_else else continue_symbol))

    print('')
    for statement in if_statement.statements:
        generate(statement, local_scope)

    if has_else:
        print('JUMP ' + continue_symbol)

    if has_else:
        print(else_symbol + ': ')
        for statement in if_statement.else_statements:
            generate(statement, local_scope)

    print(continue_symbol + ":")
    print('ADD W I ' + str((1 + local_scope.dataInStack) * 4) + ', SP')  # reset Stack Pointer


def generateVariableCreation(variable_creation, scope):
    name = variable_creation.name
    generate(variable_creation.value, scope)
    variable = scope.addData(name)

    match variable.location:
        case Location.REGISTER:
            print('MOVE W !SP, R' + str(variable.offset))
        case Location.HEAP:
            print('MOVE W hp, R13')
            print('ADD W I 4, hp')

            print('MOVE W !SP, !R13')
        case Location.STACK:
            print('SUB W I 4, SP')

    print('ADD W I 4, SP')  # reset stack pointer

def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findDataLocation(name)

    match variable.location:
        case Location.REGISTER:
            print('MOVE W !SP, R' + str(variable.offset))
        case Location.HEAP:
            print('MOVE W hp, R13')
            print('ADD W I 4, hp')

            print('MOVE W !SP, !R13')
        case Location.STACK:
            print('MOVE W !SP, ' + str((scope.dataInStack - variable.offset) * 4) + '+!SP')


def generateResolveVariable(variable, scope):
    variable = scope.findDataLocation(variable.name)

    match variable.location:
        case Location.REGISTER:
            print('MOVE W R' + str(variable.offset) + ', -!SP')
        case Location.HEAP:
            print('MOVEA heap, R13')
            print('MOVE W ' + str(variable.offset * 4) + '+!R13, -!SP')
        case Location.STACK:
            print('MOVE W ' + str((scope.dataInStack - variable.offset) * 4) + '+!SP, -!SP')


def generateBinaryOp(binary_op, scope):
    generate(binary_op.left, scope)
    generate(binary_op.right, scope)

    op = binary_op.op
    match op:
        case '+':
            print('ADD W !SP, 4+!SP')
            print('ADD W I 4, SP')
        case '-':
            print('SUB W !SP, 4+!SP')
            print('ADD W I 4, SP')
        case '*':
            print('MULT W !SP, 4+!SP')
            print('ADD W I 4, SP')
        case '/':
            print('DIV W !SP, 4+!SP')
            print('ADD W I 4, SP')
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
            print('OR W !SP, 4+!SP')
            print('ADD W I 4, SP')
        case 'and':
            print('MULT W !SP, 4+!SP')
            print('ADD W I 4, SP')


def generateComparison(op):
    mappings = {">": "JGT",
                ">=": "JGE",
                "==": "JEQ",
                "<=": "JLE",
                "<": "JLE"}
    symbol = createNewSymbol('logicalTrue')
    symbol_continue = createNewSymbol('continue')

    print('SUB W !SP, 4+!SP')
    print('ADD W I 4, SP')
    print('CMP W !SP, I 0')
    print(mappings.get(op) + ' ' + symbol)
    print('MOVE W I 0, !SP')
    print('JUMP ' + symbol_continue)
    print('')
    print(symbol + ':')
    print('MOVE W I 1, !SP')
    print('')
    print(symbol_continue + ':')


def generateConstant(constant):
    print('MOVE W I ' + str(constant.value) + ', -!SP')


def generateInit():
    return '''
SEG
MOVE W I H'10000', SP
MOVEA heap, hp

start:'''


def generateHeap():
    return '''
hp: RES 4
heap: RES 0'''
