from shared.struct import StructDefinitions
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructResolve import StructResolve


def checkType(variable_type, assignment_expr, scope):
    if type(assignment_expr) is StructCreate and variable_type != assignment_expr.name:
        raise ValueError('Wrong type')
    if type(assignment_expr) is Constant:
        if (assignment_expr.value == 'true' or assignment_expr.value == 'false') and variable_type != 'boolean':
            raise ValueError('Wrong type')
        if type(assignment_expr.value) is int and variable_type != 'int':
            raise ValueError('Wrong type')
    if type(assignment_expr) is VariableNode and variable_type != assignment_expr.type_def:
        raise ValueError('Wrong type')
    if type(assignment_expr) is StructResolve:
        variable = scope.findData(assignment_expr.name)
        if variable_type != StructDefinitions.findTypeForAttribute(variable.data.type_def, assignment_expr.attribute):
            raise ValueError('Wrong type')
    if type(assignment_expr) is BinaryOp:
        checkType(variable_type, assignment_expr.left, scope)
        checkType(variable_type, assignment_expr.right, scope)
