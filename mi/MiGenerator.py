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
    generated_code.append('HALT')
    generated_code.append(generateHeap())
    return generated_code


def generate(ast, scope):
    if type(ast) is StructNode:
        generateStruct(ast, scope)
    if type(ast) is StructCreate:
        generateStructCreate(ast, scope)
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


def generateStruct(struct, scope):
    StructDefinitions.addDefinition(struct)


def generateStructCreate(struct, scope):
    generated_code.append('MOVE W hp, R13')

    offset = 0
    for definition in StructDefinitions.findDefinition(struct.name):
        match definition.type_def:
            case 'int':
                offset += 4
            case 'boolean':
                offset += 1

    generated_code.append('ADD W I ' + str(offset) + ', hp')
    generated_code.append('MOVE W R13, !SP')


def generateStructAssignment(struct, scope):
    variable = scope.findData(struct.name)
    struct_name = variable.data.type_def
    struct_attribute = struct.attribute
    type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

    TypeCheck.checkType(type_def, struct.value, scope)
    generate(struct.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' !SP, ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + ' +!R' + str(variable.offset))
        case Location.STACK:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' !SP, ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + ' !(-' + str(variable.offset * 4) + '+!R12)')


def generateStructResolve(struct, scope):
    variable = scope.findData(struct.name)
    struct_name = variable.data.type_def
    struct_attribute = struct.attribute
    type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + '+!R' + str(variable.offset) + ', -!SP')
        case Location.STACK:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' ' + str(StructDefinitions.getOffsetForAttribute(struct_name, struct_attribute)) + ' !(-' + str(variable.offset * 4) + '+!R12), -!SP')


def generateForStatement(for_statement, scope):
    local_scope = DataAllocator(scope, scope.dataInRegister, scope.dataInStack)
    for_symbol = createNewSymbol('for')
    continue_symbol = createNewSymbol('continue')
    variable_creation_statements = findVariableCreationStatements(for_statement)

    for creation in variable_creation_statements:
        scope.addData(Variable(creation.name, creation.data.type_def))
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
        local_scope.addData(Variable(creation.name, creation.data.type_def))
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
    generate(variable_creation.value, scope)
    variable = scope.addData(Variable(name, type_def))

    TypeCheck.checkType(type_def, variable_creation.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' !SP, R' + str(variable.offset))
        case Location.STACK:
            generated_code.append('SUB W I 4, SP')

    generated_code.append('ADD W I 4, SP')  # reset stack pointer


def generateVariableAssignment(variable_assignment, scope):
    name = variable_assignment.name
    generate(variable_assignment.value, scope)
    variable = scope.findData(name)
    type_def = variable.data.type_def

    TypeCheck.checkType(variable.data.type_def, variable_assignment.value, scope)

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' !SP, R' + str(variable.offset))
        case Location.STACK:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' !SP, -' + str(variable.offset * 4) + '+!R12')

    generated_code.append('ADD W I 4, SP')


def generateResolveVariable(variable, scope):
    variable = scope.findData(variable.name)
    type_def = variable.data.type_def

    match variable.location:
        case Location.REGISTER:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' R' + str(variable.offset) + ', -!SP')
        case Location.STACK:
            generated_code.append('MOVE ' + getSpaceForType(type_def) + ' -' + str(variable.offset * 4) + '+!R12, -!SP')


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
    if constant.value == 'true':
        generated_code.append('MOVE B I 1, -!SP')
    elif constant.value == 'false':
        generated_code.append('MOVE B I 0, -!SP')
    else:
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


def getSpaceForType(type_def):
    match type_def:
        case 'int':
            return 'W'
        case 'boolean':
            return 'B'
        case _:
            return 'W'
