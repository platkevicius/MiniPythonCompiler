from shared.allocation.Data import Data
from shared.allocation.Location import Location


class RiscvAllocator:

    def __init__(self, parent, data_in_register_int, data_in_register_float, data_in_stack):
        self.parent = parent
        self.data_in_register_int = data_in_register_int
        self.data_in_register_float = data_in_register_float
        self.dataInStack = data_in_stack
        self.register = {}
        self.stack = {}

    def addData(self, data):
        if data.name in self.register or data.name in self.stack:
            raise ValueError('There is already declaration with the name: ' + data.name)
        match data.type_def:
            case 'float':
                if self.data_in_register_float != 11:
                    self.data_in_register_float += 1
                    var = Data(data, self.data_in_register_float, Location.REGISTER)
                    self.register[data.name] = var
                    return var
                else:
                    self.dataInStack += 1
                    var = Data(data, -self.dataInStack, Location.STACK)
                    self.stack[data.name] = var
                    return var
            case _:
                if self.data_in_register_int != 11:
                    self.data_in_register_int += 1
                    var = Data(data, self.data_in_register_int, Location.REGISTER)
                    self.register[data.name] = var
                    return var
                else:
                    self.dataInStack += 1
                    var = Data(data, -self.dataInStack, Location.STACK)
                    self.stack[data.name] = var
                    return var


    def findData(self, name):
        register_data = self.register.get(name, None)
        stack_data = self.stack.get(name, None)

        if register_data is not None:
            return register_data
        elif stack_data is not None:
            return stack_data
        elif self.parent is not None:
            return self.parent.findData(name)
        else:
            raise NameError('There is no Variable with name: ' + str(name) + '.')

    def getDataInStack(self):
        return self.dataInStack

    def getOffsetForLocalVariable(self):
        if self.parent is None:
            return self.dataInStack
        else:
            return self.dataInStack - self.parent.dataInStack

    def isInFunction(self):
        if self.parent is None:
            return False
        else:
            return self.parent.isInFunction()

    def getParams(self):
        if self.parent is None:
            return -1
        else:
            return self.parent.getParams()

    def findUsedRegisters(self):
        if self.parent is None:
            return -1

        return self.parent.findUsedRegisters()


