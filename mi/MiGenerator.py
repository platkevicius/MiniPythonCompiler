from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.statement.ForStatement import ForStatement
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from mi.allocation.DataAllocator import *
from mi.SymbolGenerator import createNewSymbol
from syntaxTree.statement.WhileStatement import WhileStatement

generated_code = []


def generateMachineCode(goals, scope):
    generated_code.append(generateInit())
    for goal in goals:
        generate(goal, scope)
    generated_code.append('HALT')
    generated_code.append(generateHeap())
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
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInHeap)
    for_symbol = createNewSymbol('for')
    continue_symbol = createNewSymbol('continue')

    # init index variable
    generate(VariableCreation(for_statement.index_var_name, for_statement.range_from), local_scope)
    generate(VariableCreation('!', for_statement.range_to), local_scope)

    generated_code.append('')   # formatting
    generated_code.append(for_symbol + ':')
    generate(
        BinaryOp(
            VariableNode(for_statement.index_var_name),
            '<=',
            VariableNode('!')
        ), local_scope)

    generated_code.append('ADD W I 4, SP')
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + continue_symbol)

    for statement in for_statement.statements:
        generate(statement, local_scope)

    generate(VariableAssignment(for_statement.index_var_name, BinaryOp(VariableNode(for_statement.index_var_name), '+', Constant(1))), local_scope)
    generated_code.append('JUMP ' + for_symbol)

    generated_code.append('')  # formatting
    generated_code.append(continue_symbol + ":")


def generateWhileStatement(while_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInHeap)
    while_symbol = createNewSymbol('while')
    continue_symbol = createNewSymbol('continue')

    generated_code.append('')           # formatting
    generated_code.append(while_symbol + ':')
    generate(while_statement.condition, local_scope)

    generated_code.append('ADD W I 4, SP')
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + continue_symbol)

    for statement in while_statement.statements:
        generate(statement, local_scope)

    generated_code.append('ADD W I 4, SP')  # reset Stack Pointer
    generated_code.append('JUMP ' + while_symbol)

    generated_code.append('')   # formatting
    generated_code.append(continue_symbol + ":")


def generateIfStatement(if_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInHeap)
    generate(if_statement.condition, scope)
    else_symbol = createNewSymbol('else')
    continue_symbol = createNewSymbol('continue')

    has_else = len(if_statement.else_statements) != 0

    generated_code.append('ADD W I 4, SP')
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + (else_symbol if has_else else continue_symbol))

    generated_code.append('')   # formatting
    for statement in if_statement.statements:
        generate(statement, local_scope)

    if has_else:
        generated_code.append('JUMP ' + continue_symbol)

    if has_else:
        generated_code.append(else_symbol + ': ')
        for statement in if_statement.else_statements:
            generate(statement, local_scope)

    generated_code.append(continue_symbol + ":")


def generateVariableCreation(variable_creation, scope):
    name = variable_creation.name
    generate(variable_creation.value, scope)
    variable = scope.addData(name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W !SP, R' + str(variable.offset))
        case Location.HEAP:
            generated_code.append('MOVE W hp, R13')
            generated_code.append('ADD W I 4, hp')

            generated_code.append('MOVE W !SP, !R13')
        case Location.STACK:
            generated_code.append('SUB W I 4, SP')

    generated_code.append('ADD W I 4, SP')  # reset stack pointer


def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findDataLocation(name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W !SP, R' + str(variable.offset))
        case Location.HEAP:
            generated_code.append('MOVE W hp, R13')
            generated_code.append('ADD W I 4, hp')

            generated_code.append('MOVE W !SP, !R13')
        case Location.STACK:
            generated_code.append('MOVE W !SP, ' + str((scope.dataInStack - variable.offset) * 4) + '+!SP')

    generated_code.append('ADD W I 4, SP')


def generateResolveVariable(variable, scope):
    variable = scope.findDataLocation(variable.name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W R' + str(variable.offset) + ', -!SP')
        case Location.HEAP:
            generated_code.append('MOVEA heap, R13')
            generated_code.append('MOVE W ' + str(variable.offset * 4) + '+!R13, -!SP')
        case Location.STACK:
            generated_code.append('MOVE W ' + str(variable.offset * 4) + '+!SP, -!SP')


def generateBinaryOp(binary_op, scope):
    generate(binary_op.left, scope)
    generate(binary_op.right, scope)

    op = binary_op.op
    match op:
        case '+':
            generated_code.append('ADD W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')
        case '-':
            generated_code.append('SUB W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')
        case '*':
            generated_code.append('MULT W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')
        case '/':
            generated_code.append('DIV W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')
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
            generated_code.append('OR W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')
        case 'and':
            generated_code.append('MULT W !SP, 4+!SP')
            generated_code.append('ADD W I 4, SP')


def generateComparison(op):
    mappings = {">": "JGT",
                ">=": "JGE",
                "==": "JEQ",
                "<=": "JLE",
                "<": "JLE"}
    symbol = createNewSymbol('logicalTrue')
    symbol_continue = createNewSymbol('continue')

    generated_code.append('SUB W !SP, 4+!SP')
    generated_code.append('ADD W I 4, SP')
    generated_code.append('CMP W !SP, I 0')
    generated_code.append(mappings.get(op) + ' ' + symbol)
    generated_code.append('MOVE W I 0, !SP')
    generated_code.append('JUMP ' + symbol_continue)
    generated_code.append('')
    generated_code.append(symbol + ':')
    generated_code.append('MOVE W I 1, !SP')
    generated_code.append('')
    generated_code.append(symbol_continue + ':')


def generateConstant(constant):
    generated_code.append('MOVE W I ' + str(constant.value) + ', -!SP')


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
