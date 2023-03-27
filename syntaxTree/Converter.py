from shared.variables.Variable import Variable
from syntaxTree.arrays.ArrayAssignment import ArrayAssignment
from syntaxTree.arrays.ArrayCreate import ArrayCreate
from syntaxTree.arrays.ArrayResolve import ArrayResolve
from syntaxTree.expression.BinaryOp import BinaryOp
from syntaxTree.expression.Constant import Constant
from syntaxTree.expression.VariableNode import VariableNode
from syntaxTree.function.FunctionCall import FunctionCall
from syntaxTree.function.FunctionCreate import FunctionCreate
from syntaxTree.statement.IfStatement import IfStatement
from syntaxTree.statement.ReturnStatement import ReturnStatement
from syntaxTree.statement.VariableAssignment import VariableAssignment
from syntaxTree.statement.VariableCreation import VariableCreation
from syntaxTree.statement.LoopStatement import LoopStatement
from syntaxTree.struct.StructAssignment import StructAssignment
from syntaxTree.struct.StructCreate import StructCreate
from syntaxTree.struct.StructNode import StructNode
from syntaxTree.struct.StructResolve import StructResolve


# transforms a parse tree from lark to an ast for code generation
def parse_tree_to_ast(e):
    if e.data == 'goal':
        ast = []
        for child in e.children:
            gen = parse_tree_to_ast(child)
            if type(gen) == list:
                ast.extend(gen)
            else:
                ast.append(gen)

        return ast
    if e.data == 'number':
        try:
            val = Constant(int(e.children[0]))
            return val
        except ValueError:
            return Constant(float(e.children[0].value))
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
    elif e.data == 'array_create':
        type_def = e.children[0]
        dimensions = {}

        for i in range(1, len(e.children)):
            dimensions[i-1] = parse_tree_to_ast(e.children[i])
        return ArrayCreate(type_def.data + ('[]'*len(dimensions)), dimensions)
    elif e.data == 'array_indexing':
        name = e.children[0]
        dimensions = {}

        for i in range(1, len(e.children)):
            dimensions[i] = parse_tree_to_ast(e.children[i])
        return ArrayResolve(name, dimensions)
    elif e.data == 'array_assignment':
        name = e.children[0]
        dimensions = {}

        for i in range(1, len(e.children)-1):
            dimensions[i] = parse_tree_to_ast(e.children[i])
        return ArrayAssignment(name, dimensions, parse_tree_to_ast(e.children[len(e.children)-1]))
    elif e.data == 'variable_creation':
        name, type_def, expr = e.children
        if type_def.data == 'struct':
            type_def = type_def.children[0]
        elif type_def.data == 'array':
            child = type_def.children[0]
            type_def = child.data + '[]'*(len(type_def.children)-1)
        else:
            type_def = type_def.data
        return VariableCreation(name, type_def, parse_tree_to_ast(expr))
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
            gen = parse_tree_to_ast(e.children[i])

            if type(gen) == list:
                statements.extend(gen)
            else:
                statements.append(gen)
        return LoopStatement(parse_tree_to_ast(e.children[0]), statements)
    elif e.data == 'for':
        statements = []
        begin = e.children[0]

        for i in range(3, len(e.children)):
            statements.append(parse_tree_to_ast(e.children[i]))

        statements.append(VariableAssignment(begin, BinaryOp(VariableNode(begin), '+', Constant(1))))

        varCreate = VariableCreation(e.children[0], 'int', parse_tree_to_ast(e.children[1]))
        whileStmt = LoopStatement(
                    BinaryOp(VariableNode(e.children[0]), '<', parse_tree_to_ast(e.children[2])),
                    statements)

        return [varCreate, whileStmt]
    elif e.data == 'struct':
        name, body = e.children
        return StructNode(name, parse_tree_to_ast(body))
    elif e.data == 'struct_body':
        definitions = []

        for i in range(0, len(e.children), 2):
            definitions.append(Variable(e.children[i], e.children[i + 1].data))
        return definitions
    elif e.data == 'struct_create':
        name = e.children[0]
        return StructCreate(name)
    elif e.data == 'struct_assignment':
        name, attribute, value = e.children
        return StructAssignment(name, attribute, parse_tree_to_ast(value))
    elif e.data == 'struct_resolve':
        name, attribute = e.children
        return StructResolve(name, attribute)
    elif e.data == 'true' or e.data == 'false':
        return Constant(e.data)
    elif e.data == 'function':
        name = e.children[0]
        params = []
        statements = []

        for i in range(0, len(e.children[1].children), 2):
            params.append(Variable(e.children[1].children[i], e.children[1].children[i+1].data))

        return_type = e.children[2].data

        for i in range(3, len(e.children)):
            gen = parse_tree_to_ast(e.children[i])

            if type(gen) == list:
                statements.extend(gen)
            else:
                statements.append(gen)

        return FunctionCreate(name, params, return_type, statements)
    elif e.data == 'function_call':
        name = e.children[0]
        params = []

        for i in range(1, len(e.children)):
            params.append(parse_tree_to_ast(e.children[i]))

        return FunctionCall(name, params)
    elif e.data == 'return':
        return ReturnStatement(parse_tree_to_ast(e.children[0]))
