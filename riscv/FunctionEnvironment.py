from shared.allocation.Data import Data
from shared.allocation.Location import Location


class FunctionEnvironment:

    def __init__(self, parent):
        self.parent = parent
        self.dataInRegister = 11
        self.dataInStack = 0
        self.stack = {}
        self.paramOffset = 0

    def addParam(self, data):
        if data.name in self.stack:
            raise ValueError('There is already declaration with the name: ' + data.name)

        var = Data(data, self.paramOffset, Location.REGISTER)
        self.stack[data.name] = var
        self.paramOffset += 1

    def addData(self, data):
        if data.name in self.stack:
            raise ValueError('There is already declaration with the name: ' + data.name)

        self.dataInStack += 1
        var = Data(data, -self.dataInStack, Location.STACK)
        self.stack[data.name] = var
        return var

    def findData(self, name):
        stack_data = self.stack.get(name, None)

        if stack_data is not None:
            offset = 1
            if self.parent is not None:
                offset = self.parent.dataInStack

            stack_data.offset = offset + stack_data.offset
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
        return True
