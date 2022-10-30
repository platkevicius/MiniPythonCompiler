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
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    for_symbol = createNewSymbol('for')
    continue_symbol = createNewSymbol('continue')
    variable_creation_statements = findVariableCreationStatements(for_statement)

    for creation in variable_creation_statements:
        scope.addData(creation.name)
        generated_code.append('SUB W I 4, SP')

    # init index variable
    generate(VariableCreation(for_statement.index_var_name, 'int', for_statement.range_from), local_scope)
    generate(VariableCreation('!', 'int', for_statement.range_to), local_scope)

    generated_code.append('')   # formatting
    generated_code.append(for_symbol + ':')
    generate(
        BinaryOp(
            VariableNode(for_statement.index_var_name),
            '<=',
            VariableNode('!')
        ), local_scope)

    generated_code.append('ADD W I 4, SP')  # reset Stack Pointer from logical calculation in Stack
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + continue_symbol)

    for statement in for_statement.statements:
        if type(statement) is VariableCreation:
            generate(VariableAssignment(statement.name, statement.value), local_scope)
            continue

        generate(statement, local_scope)

    generate(VariableAssignment(for_statement.index_var_name, BinaryOp(VariableNode(for_statement.index_var_name), '+', Constant(1))), local_scope)
    generated_code.append('JUMP ' + for_symbol)

    generated_code.append('')  # formatting
    generated_code.append(continue_symbol + ":")
    generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer


def generateWhileStatement(while_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    while_symbol = createNewSymbol('while')
    continue_symbol = createNewSymbol('continue')
    variable_creation_statements = findVariableCreationStatements(while_statement)

    for creation in variable_creation_statements:
        local_scope.addData(creation.name)
        generated_code.append('SUB W I 4, SP')

    generated_code.append('')           # formatting
    generated_code.append(while_symbol + ':')
    generate(while_statement.condition, local_scope)

    generated_code.append('ADD W I 4, SP')  # reset Stack Pointer from logical calculation in Stack
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + continue_symbol)

    for statement in while_statement.statements:
        if type(statement) is VariableCreation:
            generate(VariableAssignment(statement.name, statement.value), local_scope)
            continue

        generate(statement, local_scope)

    generated_code.append('JUMP ' + while_symbol)

    generated_code.append('')   # formatting
    generated_code.append(continue_symbol + ":")
    generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer


def generateIfStatement(if_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    else_symbol = createNewSymbol('else')
    continue_symbol = createNewSymbol('continue')

    has_else = len(if_statement.else_statements) != 0

    generate(if_statement.condition, scope)
    generated_code.append('ADD W I 4, SP')      # reset Stack Pointer from logical calculation in Stack
    generated_code.append('CMP W I 1, -4+!SP')
    generated_code.append('JNE ' + (else_symbol if has_else else continue_symbol))

    generated_code.append('')   # formatting
    for statement in if_statement.statements:
        generate(statement, local_scope)

    if has_else:
        generated_code.append('JUMP ' + continue_symbol)
        generated_code.append(else_symbol + ': ')
        for statement in if_statement.else_statements:
            generate(statement, local_scope)

    generated_code.append(continue_symbol + ":")
    generated_code.append('ADD W I ' + str(local_scope.getDataInStack() * 4) + ', SP')  # reset Stack Pointer


def generateVariableCreation(variable_creation, scope):
    name = variable_creation.name
    type_def = variable_creation.type_def

    TypeCheck.checkType(type_def, variable_creation.value, scope)

    generate(variable_creation.value, scope)
    variable = scope.addData(Variable(name, type_def))

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W !SP, R' + str(variable.offset))
        case Location.STACK:
            generated_code.append('SUB W I 4, SP')

    generated_code.append('ADD W I 4, SP')  # reset stack pointer


def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findData(name)

    TypeCheck.checkType(variable.data.type_def, variable_assignment.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W !SP, R' + str(variable.offset))
        case Location.STACK:
            generated_code.append('MOVE W !SP, -' + str(variable.offset * 4) + '+!R12')

    generated_code.append('ADD W I 4, SP')


def generateResolveVariable(variable, scope):
    variable = scope.findData(variable.name)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE W R' + str(variable.offset) + ', -!SP')
        case Location.STACK:
            generated_code.append('MOVE W -' + str(variable.offset * 4) + '+!R12, -!SP')


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
MOVE W I H'10000', R12
MOVEA heap, hp

start:'''


def generateHeap():
    return '''
hp: RES 4
heap: RES 0'''


def findVariableCreationStatements(ast):
    statements = []
    for statement in ast.statements:
        if type(statement) is VariableCreation:
            statements.append(statement)
    return statements
