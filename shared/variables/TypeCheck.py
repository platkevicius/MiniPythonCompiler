from syntaxTree.expression import BinaryOp
from syntaxTree.expression.VariableNode import VariableNode


def checkType(variable_type, assignment_expr, scope):
    if type(assignment_expr) is BinaryOp:
        op = assignment_expr.op
        if variable_type == 'int' and (op != '+' and op != '-' and op != '*' and op != '/'):
            raise ValueError('Type error, value is not proper for an integer')
        if variable_type == 'boolean' and (op != 'or' and op != 'and' and op != ">=" and op != ">" and op != "=" and op != "<=" and op != "<" and op != "True" and op != "False"):
            raise ValueError('Type error, value is not proper for an boolean')
    if type(assignment_expr) is VariableNode:
        variable = scope.findData(assignment_expr.name)
        if variable.data.type_def is not variable_type:
            raise ValueError('wrong types')
