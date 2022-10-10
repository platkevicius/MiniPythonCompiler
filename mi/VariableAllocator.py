from mi.Variable import Variable

# globals to keep track of variables in register and heap
variablesInRegister = 0
variablesInHeap = 0

register = {}
heap = {}


def addVariable(name):
    global variablesInRegister
    global variablesInHeap
    global register
    global heap

    if variablesInRegister != 13:
        register[name] = variablesInRegister
        variablesInRegister += 1
        return Variable(name, variablesInRegister - 1, True)
    else:
        heap[name] = variablesInHeap
        variablesInHeap += 1
        return Variable(name, variablesInHeap - 1, False)


def findVariableLocation(name):
    global register
    global heap

    register_value = register.get(name, None)
    heap_value = heap.get(name, None)

    if register_value is not None:
        return Variable(name, register_value, True)
    elif heap_value is not None:
        return Variable(name, heap_value, False)
    else:
        raise NameError('There is no Variable with name: ' + name + '.')
