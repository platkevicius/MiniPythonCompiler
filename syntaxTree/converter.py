from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant


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