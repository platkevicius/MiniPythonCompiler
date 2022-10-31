from syntaxTree.expression import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.struct.StructCreate import StructCreate


def checkType(variable_type, assignment_expr, scope):
    if type(assignment_expr) is Constant:
        if variable_type == 'boolean' and (assignment_expr.value != 'true' and assignment_expr.value != 'false'):
            raise ValueError('Type error')
        elif variable_type == 'int' and type(assignment_expr.value) != int:
            raise ValueError('Type error')
    if type(assignment_expr) is BinaryOp:
        op = assignment_expr.op
        if variable_type == 'int' and (op != '+' and op != '-' and op != '*' and op != '/'):
            raise ValueError('Type error, value is not proper for an integer')
        if variable_type == 'boolean' and (op != 'or' and op != 'and' and op != ">=" and op != ">" and op != "=" and op != "<=" and op != "<"):
            raise ValueError('Type error, value is not proper for an boolean')
    elif type(assignment_expr) is VariableNode:
        data = scope.findData(assignment_expr.name)

        if data.data.type_def is not variable_type:
            raise ValueError('wrong types')
    elif type(assignment_expr) is StructCreate:
        if assignment_expr.name != variable_type:
            raise ValueError('wrong types ' + assignment_expr.name + ' != ' + variable_type)
