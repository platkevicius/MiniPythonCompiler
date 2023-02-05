from shared.function import FunctionDefinitions
from shared.struct import StructDefinitions
from shared.variables.Variable import Variable
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructResolve import StructResolve


def resolveType(ast, scope):
    if type(ast) is FunctionCall:
        return checkFunctionCall(ast)
    if type(ast) is StructCreate:
        return checkStructCreate(ast)
    if type(ast) is StructResolve:
        return checkStructResolve(ast, scope)
    elif type(ast) is BinaryOp:
        return checkBinaryOp(ast, scope)
    elif type(ast) is Constant:
        return checkConstant(ast)
    elif type(ast) is VariableNode:
        return checkResolveVariable(ast, scope)


def checkFunctionCall(ast):
    name = ast.name
    function = FunctionDefinitions.findDefinition(name)

    return function.return_type


def checkStructCreate(ast):
    return ast.name


def checkStructResolve(ast, scope):
    variable = scope.findData(ast.name)
    return StructDefinitions.findTypeForAttribute(variable.data.type_def, ast.attribute)


def checkVariableCreation(ast, scope):
    name = ast.name
    type_def = ast.type_def
    scope.addData(Variable(name, type_def))


def checkBinaryOp(ast, scope):
    var_type1 = resolveType(ast.left, scope)
    var_type2 = resolveType(ast.right, scope)

    if var_type1 == 'float' and var_type2 == 'int':
        var_type2 = 'float'
        if type(ast.right) == Constant:
            ast.right.type_def = 'float'

    if var_type1 == 'int' and var_type2 == 'float':
        var_type1 = 'float'

        if type(ast.left) == Constant:
            ast.right.type_def = 'float'

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
            type_def = resolveType(assigment_expr, scope)
            if assigment_expr.op in logicals:
                return 'boolean'
            elif assigment_expr.op in arithmetics:
                return type_def
        case _:
            return resolveType(assigment_expr, scope)
