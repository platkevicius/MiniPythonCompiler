symbols = {}


def createNewSymbol(prefix):
    count = symbols.get(prefix, 0)
    symbols[prefix] = count + 1

    return prefix + str(count)
