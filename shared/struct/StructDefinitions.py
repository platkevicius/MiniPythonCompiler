definitions = {}


def addDefinition(struct):
    definitions[struct.name] = struct.definitions


def findDefinition(name):
    return definitions[name]