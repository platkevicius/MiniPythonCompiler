from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant


def optimizeBinaryOp(expr):
    if type(expr) is BinaryOp:
        expr1 = optimizeBinaryOp(expr.left)
        expr2 = optimizeBinaryOp(expr.right)
        op = expr.op

        match op:
            case '+':
                return expr1 + expr2
            case '-':
                return expr1 - expr2
            case '*':
                return expr1 * expr2
            case '/':
                return expr1 / expr2
    elif type(expr) is Constant:
        return expr.value
