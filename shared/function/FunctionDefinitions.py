definitions = {}


def addDefinition(function):
    definitions[function.name] = function


def findDefinition(name):
    return definitions[name]


def countFloatParams(name):
    function = findDefinition(name)
    count = 0
    for param in function.params:
        if param.type_def == 'float':
            count += 1
    return count


def countNonFloatParams(name):
    function = findDefinition(name)
    count = 0
    for param in function.params:
        if param.type_def != 'float':
            count += 1
    return count


def findTypeForParam(function_name, param_name):
    function = definitions[function_name]

    for param in function.params:
        if param.name is param_name:
            return param.type_def

    raise ValueError('No param with name: ' + param_name + ' in function: ' + function_name)
