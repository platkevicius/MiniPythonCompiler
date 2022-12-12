from shared.allocation.Data import Data
from shared.allocation.Location import Location


class MiAllocator:

    def __init__(self, parent, data_in_register, data_in_stack):
        self.parent = parent
        self.dataInRegister = data_in_register
        self.dataInStack = data_in_stack
        self.register = {}
        self.stack = {}

    def addData(self, data):
        if data.name in self.register or data.name in self.stack:
            raise ValueError('There is already declaration with the name: ' + data.name)
        if self.dataInRegister != 11:
            var = Data(data, self.dataInRegister, Location.REGISTER)
            self.register[data.name] = var
            self.dataInRegister += 1
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
