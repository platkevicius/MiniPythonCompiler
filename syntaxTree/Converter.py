from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation


def parse_tree_to_ast(e):
    if e.data == 'goal':
        ast = []
        for child in e.children:
            ast.append(parse_tree_to_ast(child))
        return ast
    if e.data == 'number':
        return Constant(int(e.children[0].value))
    if e.data == 'add':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '+', parse_tree_to_ast(e2))
    elif e.data == 'minus':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '-', parse_tree_to_ast(e2))
    elif e.data == 'mult':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '*', parse_tree_to_ast(e2))
    elif e.data == 'div':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '/', parse_tree_to_ast(e2))
    elif e.data == 'term':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'factor':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'primary':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'grouping':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'variable_creation':
        name, expr = e.children
        return VariableCreation(name, parse_tree_to_ast(expr))
    elif e.data == 'variable_assignment':
        name, expr = e.children
        return VariableAssignment(name, parse_tree_to_ast(expr))
    elif e.data == 'variable':
        return VariableNode(e.children[0].value)
