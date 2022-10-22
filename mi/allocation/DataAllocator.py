from mi.allocation.Data import Data
from mi.allocation.Location import Location


class DataAllocator:

    def __init__(self, parent, data_in_register, data_in_stack):
        self.parent = parent
        self.dataInRegister = data_in_register
        self.dataInStack = data_in_stack
        self.register = {}
        self.stack = {}

    def addData(self, name):
        if self.register.__contains__(name) or self.stack.__contains__(name):
            raise ValueError('There is already a variable declared with the name: ' + name)

        if self.dataInRegister != 12:
            self.register[name] = self.dataInRegister
            self.dataInRegister += 1
            return Data(name, self.dataInRegister - 1, Location.REGISTER)
        else:
            self.stack[name] = self.dataInStack
            self.dataInStack += 1
            return Data(name, self.dataInStack - 1, Location.HEAP)

    def findDataLocation(self, name):
        register_value = self.register.get(name, None)
        stack_value = self.stack.get(name, None)

        if register_value is not None:
            return Data(name, register_value, Location.REGISTER)
        elif stack_value is not None:
            return Data(name, stack_value, Location.STACK)
        elif self.parent is not None:
            return self.parent.findDataLocation(name)
        else:
            raise NameError('There is no Variable with name: ' + name + '.')

    def getDataInStack(self):
        if self.parent is None:
            return self.dataInStack
        else:
            return self.dataInStack - self.parent.dataInStack
