from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant


def generateMi(goals):
    print(generateInit())
    for goal in goals:
        generate(goal)
    print('HALT')
    print(generateHeap())


def generate(ast):
    if type(ast) is BinaryOp:
        generateBinaryOp(ast)
    elif type(ast) is Constant:
        generateConstant(ast)


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

    # reset SP based on BinaryOp
    print('ADD W I 4, SP')


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
