from shared.struct import StructDefinitions
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructResolve import StructResolve


def checkTypeForVariable(variable_type, assignment_expr, scope):
    match assignment_expr:
        # general check on type fast fail
        case BinaryOp():
            checkLogical(variable_type, assignment_expr)
            checkArithmetic(variable_type, assignment_expr)

    var_type = checkForSubExpressions(variable_type, assignment_expr, scope)

    if type(assignment_expr) != BinaryOp:
        if var_type != variable_type:
            raise ValueError('Wrong types')


def checkForSubExpressions(variable_type, assignment_expr, scope):
    match assignment_expr:
        case BinaryOp():
            var_type1 = checkForSubExpressions(variable_type, assignment_expr.left, scope)
            var_type2 = checkForSubExpressions(variable_type, assignment_expr.right, scope)

            if var_type1 != var_type2:
                raise ValueError('Wrong types')
            return var_type1
        case VariableNode():
            variable = scope.findData(assignment_expr.name)
            return variable.data.type_def
        case StructResolve():
            variable = scope.findData(assignment_expr.name)
            return StructDefinitions.findTypeForAttribute(variable.data.type_def, assignment_expr.attribute)
        case StructCreate():
            return assignment_expr.name
        case Constant():
            if assignment_expr.value == 'true' or assignment_expr.value == 'false':
                return 'boolean'
            if type(assignment_expr.value) == int:
                return 'int'


def checkLogical(variable_type, assigment_expr):
    logicals = ['or', 'and', '<', '<=', '=', '>=', '>']
    if assigment_expr.op in logicals and variable_type != 'boolean':
        raise ValueError('Wrong type')


def checkArithmetic(variable_type, assigment_expr):
    arithmetics = ['+', '-', '*', '/']
    if assigment_expr.op in arithmetics and variable_type != 'int':
        raise ValueError('Wrong type')
