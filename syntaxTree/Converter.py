from shared.variables.Variable import Variable
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.statement.ForStatement import ForStatement
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.statement.WhileStatement import WhileStatement


# transforms a parse tree from lark to an ast for code generation
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode


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
    elif e.data == 'or':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), 'or', parse_tree_to_ast(e2))
    elif e.data == 'and':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), 'and', parse_tree_to_ast(e2))
    elif e.data == 'greater':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '>', parse_tree_to_ast(e2))
    elif e.data == 'greater_equals':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '>=', parse_tree_to_ast(e2))
    elif e.data == 'equals':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '==', parse_tree_to_ast(e2))
    elif e.data == 'less':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '<', parse_tree_to_ast(e2))
    elif e.data == 'less_equals':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '<=', parse_tree_to_ast(e2))
    elif e.data == 'not_equals':
        e1, e2 = e.children
        return BinaryOp(parse_tree_to_ast(e1), '!=', parse_tree_to_ast(e2))
    elif e.data == 'term':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'factor':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'primary':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'grouping':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'comparison':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'conjunction':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'variable_creation':
        name, type_def, expr = e.children
        if type_def.data == 'struct':
            type_def = type_def.children[0]
            return VariableCreation(name, type_def, parse_tree_to_ast(expr))
        return VariableCreation(name, type_def.data, parse_tree_to_ast(expr))
    elif e.data == 'variable_assignment':
        name, expr = e.children
        return VariableAssignment(name, parse_tree_to_ast(expr))
    elif e.data == 'variable':
        return VariableNode(e.children[0].value)
    elif e.data == 'sum':
        return parse_tree_to_ast(e.children[0])
    elif e.data == 'if':
        statements = []
        elseStatements = []
        for i in range(1, len(e.children)):
            if e.children[i].data == 'else_statement':
                elseStatements = parse_tree_to_ast(e.children[i])
                continue
            statements.append(parse_tree_to_ast(e.children[i]))
        return IfStatement(parse_tree_to_ast(e.children[0]), statements, elseStatements)
    elif e.data == 'else_statement':
        statements = []
        for child in e.children:
            statements.append(parse_tree_to_ast(child))
        return statements
    elif e.data == 'while':
        statements = []
        for i in range(1, len(e.children)):
            statements.append(parse_tree_to_ast(e.children[i]))
        return WhileStatement(parse_tree_to_ast(e.children[0]), statements)
    elif e.data == 'for':
        statements = []
        for i in range(3, len(e.children)):
            statements.append(parse_tree_to_ast(e.children[i]))
        return ForStatement(
            e.children[0],
            parse_tree_to_ast(e.children[1]),
            parse_tree_to_ast(e.children[2]),
            statements
        )
    elif e.data == 'struct':
        name, body = e.children
        return StructNode(name, parse_tree_to_ast(body))
    elif e.data == 'struct_body':
        definitions = []

        for i in range(0, len(e.children), 2):
            definitions.append(Variable(e.children[i], e.children[i+1].data))
        return definitions
    elif e.data == 'struct_create':
        name = e.children[0]
        return StructCreate(name)
