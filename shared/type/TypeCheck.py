from mi.FunctionEnvironment import FunctionEnvironment
from mi.MiAllocator import MiAllocator
from shared.function import FunctionDefinitions
from shared.function.Function import Function
from shared.struct import StructDefinitions
from shared.variables.Variable import Variable
from syntaxTree.arrays.ArrayAssignment import ArrayAssignment
from syntaxTree.arrays.ArrayCreate import ArrayCreate
from syntaxTree.arrays.ArrayIndexing import ArrayIndexing
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.function.FunctionCreate import FunctionCreate
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.LoopStatement import LoopStatement
from syntaxTree.statement.ReturnStatement import ReturnStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve


def typePass(goals):
    definitions = []
    scope = MiAllocator(None, 0, 0)
    for goal in goals:
        if type(goal) is FunctionCreate or type(goal) is StructNode:
            definitions.append(goal)
            checkType(goal, scope)

    goals = [x for x in goals if x not in definitions]
    for goal in goals:
        checkType(goal, scope)


def checkType(ast, scope):
    if type(ast) is FunctionCreate:
        return checkFunctionCreate(ast, scope)
    if type(ast) is FunctionCall:
        return checkFunctionCall(ast, scope)
    if type(ast) is ReturnStatement:
        return checkReturnStatement(ast, scope)
    if type(ast) is StructNode:
        return checkStruct(ast)
    if type(ast) is ArrayCreate:
        return checkArrayCreate(ast)
    if type(ast) is ArrayAssignment:
        pass
    if type(ast) is ArrayIndexing:
        pass
    if type(ast) is StructCreate:
        return checkStructCreate(ast)
    if type(ast) is StructAssignment:
        return checkStructAssignment(ast, scope)
    if type(ast) is StructResolve:
        return checkStructResolve(ast, scope)
    if type(ast) is LoopStatement:
        return checkLoopStatement(ast, scope)
    if type(ast) is IfStatement:
        return checkIfStatement(ast, scope)
    if type(ast) is VariableCreation:
        return checkVariableCreation(ast, scope)
    if type(ast) is VariableAssignment:
        return checkVariableAssignment(ast, scope)
    elif type(ast) is BinaryOp:
        return checkBinaryOp(ast, scope)
    elif type(ast) is Constant:
        return checkConstant(ast)
    elif type(ast) is VariableNode:
        return checkResolveVariable(ast, scope)


def checkFunctionCreate(ast, scope):
    name = ast.name
    return_type = ast.return_type
    params = ast.params_list

    FunctionDefinitions.addDefinition(Function(name, params, return_type))

    param_scope = FunctionEnvironment(scope)

    for param in ast.params_list:
        param_scope.addParam(param)
    param_scope.addParam(Variable('return', return_type))

    body_scope = FunctionEnvironment(param_scope)
    for statement in ast.statements:
        checkType(statement, body_scope)


def checkFunctionCall(ast, scope):
    name = ast.name
    function = FunctionDefinitions.findDefinition(name)

    for i in range(len(function.params)):
        param_type = FunctionDefinitions.findTypeForParam(function.name, function.params[i].name)
        expr_type = checkType(ast.params[i], scope)

        if param_type != expr_type:
            raise ValueError('Wrong types')

    return function.return_type


def checkReturnStatement(ast, scope):
    return_data = scope.findData('return')
    type_def = return_data.data.type_def
    expr_type = checkType(ast.expression, scope)

    if type_def != expr_type:
        raise ValueError('Wrong types')


def checkArrayCreate(ast):
    pass


def checkStruct(ast):
    StructDefinitions.addDefinition(ast)


def checkStructCreate(ast):
    return ast.name


def checkStructAssignment(ast, scope):
    variable = scope.findData(ast.name)
    struct_name = variable.data.type_def
    struct_attribute = ast.attribute
    type_def = StructDefinitions.findTypeForAttribute(struct_name, struct_attribute)
    expr_type = checkType(ast.value, scope)

    if type_def != expr_type:
        raise ValueError('Wrong types')


def checkStructResolve(ast, scope):
    variable = scope.findData(ast.name)
    return StructDefinitions.findTypeForAttribute(variable.data.type_def, ast.attribute)


def checkLoopStatement(ast, scope):
    local_scope = MiAllocator(scope, scope.dataInRegister, scope.dataInStack)
    expr_type = checkType(ast.condition, scope)

    if expr_type != 'boolean':
        raise ValueError('Wrong types')

    for statement in ast.statements:
        checkType(statement, local_scope)


def checkIfStatement(ast, scope):
    local_scope = MiAllocator(scope, scope.dataInRegister, scope.dataInStack)
    expr_type = checkType(ast.condition, scope)
    has_else = len(ast.else_statements) != 0

    if expr_type != 'boolean':
        raise ValueError('Wrong types')

    for statement in ast.statements:
        checkType(statement, local_scope)

    if has_else:
        for statement in ast.else_statements:
            checkType(statement, local_scope)


def checkVariableCreation(ast, scope):
    name = ast.name
    type_def = ast.type_def
    scope.addData(Variable(name, type_def))
    expr_type = getVariableValueType(ast.value, scope)

    if type_def != expr_type:
        raise ValueError('Wrong types')


def checkVariableAssignment(ast, scope):
    name = ast.name
    variable = scope.findData(name)
    type_def = variable.data.type_def
    expr_type = getVariableValueType(ast.value, scope)

    if type_def != expr_type:
        raise ValueError('Wrong types')


def checkBinaryOp(ast, scope):
    var_type1 = checkType(ast.left, scope)
    var_type2 = checkType(ast.right, scope)

    if var_type1 == 'float' and var_type2 == 'int':
        var_type2 = 'float'
        if type(ast.right) == Constant:
            ast.right.type_def = 'float'

    if var_type1 == 'int' and var_type2 == 'float':
        var_type1 = 'float'

        if type(ast.left) == Constant:
            ast.right.type_def = 'float'

    if var_type1 != var_type2:
        raise ValueError('Wrong types')

    logicals = ['<', '<=', '==', '>=', '>']
    if ast.op in logicals:
        return 'boolean'

    return var_type1


def checkConstant(ast):
    if ast.value == 'true' or ast.value == 'false':
        return 'boolean'
    if type(ast.value) == int:
        return 'int'
    if type(ast.value) == float:
        return 'float'


def checkResolveVariable(ast, scope):
    variable = scope.findData(ast.name)
    return variable.data.type_def


def getVariableValueType(assigment_expr, scope):
    logicals = ['or', 'and', '<', '<=', '==', '>=', '>']
    arithmetics = ['+', '-', '*', '/']

    match assigment_expr:
        case BinaryOp():
            type_def = checkType(assigment_expr, scope)
            if assigment_expr.op in logicals:
                return 'boolean'
            elif assigment_expr.op in arithmetics:
                return type_def
        case _:
            return checkType(assigment_expr, scope)

