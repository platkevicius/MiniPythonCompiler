definitions = {}


def addDefinition(struct):
    definitions[struct.name] = struct.definitions


def findDefinition(name):
    return definitions[name]


def findTypeForAttribute(name, attribute):
    for definition in definitions[name]:
        if definition.name == attribute:
            return definition.type_def


def getOffsetForAttribute(name, attribute):
    struct = definitions[name]

    offset = 0
    for value in struct:
        if value.name != attribute:
            offset += getOffsetForType(value.type_def)
        else:
            return offset


def getOffsetForType(type_def):
    match type_def:
        case 'int':
            return 4
        case 'boolean':
            return 1
