from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from mi.VariableAllocator import *
from mi.SymbolGenerator import createNewSymbol


def generateMachineCode(goals):
    print(generateInit())
    for goal in goals:
        generate(goal)
    print('HALT')
    print(generateHeap())


def generate(ast):
    if type(ast) is IfStatement:
        generateIfStatement(ast)
    if type(ast) is VariableCreation:
        generateVariableCreation(ast)
    if type(ast) is VariableAssignment:
        generateVariableAssignment(ast)
    elif type(ast) is BinaryOp:
        generateBinaryOp(ast)
    elif type(ast) is Constant:
        generateConstant(ast)
    elif type(ast) is VariableNode:
        generateResolveVariable(ast)


def generateIfStatement(if_statement):
    generate(if_statement.condition)
    else_symbol = createNewSymbol('else')

    print('CMP W I 1, !SP')
    print('JNE ' + else_symbol)

    print('')
    for statement in if_statement.statements:
        generate(statement)
    print('')
    print(else_symbol + ': ')
    print('ADD W I 0, R0')  # this is added due to labels not being able to stay standalone
    print('')
    for statement in if_statement.else_statements:
        generate(statement)


def generateVariableCreation(variable_creation):
    name = variable_creation.name
    generate(variable_creation.value)
    variable = addVariable(name)

    if variable.in_register:
        print('MOVE W !SP, R' + str(variable.location))
    else:
        print('MOVE W hp, R13')
        print('ADD W I 4, hp')

        print('MOVE W !SP, !R13')


def generateVariableAssignment(variable_assignment):
    name = variable_assignment.name
    generate(variable_assignment.value)
    variable = findVariableLocation(name)

    if variable.in_register:
        print('MOVE W !SP, R' + str(variable.location))
    else:
        print('MOVE W hp, R13')
        print('ADD W I 4, hp')

        print('MOVE W !SP, !R13')


def generateBinaryOp(binary_op):
    generate(binary_op.left)
    generate(binary_op.right)

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


def generateResolveVariable(variable):
    variableLocation = findVariableLocation(variable.name)

    if variableLocation.in_register:
        print('MOVE W R' + str(variableLocation.location) + ', -!SP')
    else:
        print('MOVEA heap, R13')
        print('MOVE W ' + str(variableLocation.location * 4) + '+!R13, -!SP')


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
