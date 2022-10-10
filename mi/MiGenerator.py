from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.statement.VariableCreation import VariableCreation
from mi.VariableAllocator import *


def generateMachineCode(goals):
    print(generateInit())
    for goal in goals:
        generate(goal)
    print('HALT')
    print(generateHeap())


def generate(ast):
    if type(ast) is VariableCreation:
        generateVariableCreation(ast)
    elif type(ast) is BinaryOp:
        generateBinaryOp(ast)
    elif type(ast) is Constant:
        generateConstant(ast)
    elif type(ast) is VariableNode:
        generateResolveVariable(ast)


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


def generateBinaryOp(binary_op):
    generate(binary_op.left)
    generate(binary_op.right)

    op = binary_op.op
    match op:
        case '+':
            print('ADD W !SP, 4+!SP')
        case '-':
            print('SUB W !SP, 4+!SP')
        case '*':
            print('MULT W !SP, 4+!SP')
        case '/':
            print('DIV W !SP, 4+!SP')

    # stack value has been merged into previous with given BinaryOp
    print('ADD W I 4, SP')


def generateConstant(constant):
    print('MOVE W I ' + str(constant.value) + ', -!SP')


def generateResolveVariable(variable):
    variableLocation = findVariableLocation(variable.name)

    if variableLocation.in_register:
        print('MOVE W R' + str(variableLocation.location) + ', -!SP')
    else:
        print ('MOVEA heap, R13')
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
