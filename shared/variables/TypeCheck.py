from shared.struct import StructDefinitions
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructResolve import StructResolve


def checkTypeForVariable(variable_type, assignment_expr, scope):
    match assignment_expr:
        case BinaryOp():
            checkLogical(variable_type, assignment_expr)
            checkArithmetic(variable_type, assignment_expr)
        case _:
            checkForSubExpressions(variable_type, assignment_expr, scope)


def checkForSubExpressions(variable_type, assignment_expr, scope):
    match type(assignment_expr):
        case BinaryOp():
            checkForSubExpressions(variable_type, assignment_expr.left, scope)
            checkForSubExpressions(variable_type, assignment_expr.right, scope)
        case VariableNode():
            variable = scope.findData(assignment_expr.name)
            if variable_type != variable.data.type_def:
                raise ValueError('Wrong type')
        case StructResolve():
            variable = scope.findData(assignment_expr.name)
            if variable_type != StructDefinitions.findTypeForAttribute(variable.data.type_def, assignment_expr.attribute):
                raise ValueError('Wrong type')
        case StructCreate():
            if variable_type != assignment_expr.name:
                raise ValueError('Wrong type')
        case Constant():
            if assignment_expr.value == 'true' or assignment_expr.value == 'false' and variable_type != 'boolean':
                raise ValueError('Wrong type')
            if type(assignment_expr.value) == int and variable_type != 'int':
                raise ValueError('Wrong Type')


def checkLogical(variable_type, assigment_expr):
    logicals = ['or', 'and', '<', '<=', '=', '>=', '>']
    if assigment_expr.op in logicals and variable_type != 'boolean':
        raise ValueError('Wrong type')


def checkArithmetic(variable_type, assigment_expr):
    arithmetics = ['+', '-', '*', '/']
    if assigment_expr.op in arithmetics and variable_type != 'int':
        raise ValueError('Wrong type')
