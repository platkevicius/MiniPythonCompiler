from mi.allocation.Data import Data
from mi.allocation.Location import Location


class LocalScope:
    def __init__(self, parent):
        self.parent = parent
        self.dataInStack = 0
        self.stack = {}

    def addData(self, name):
        if self.stack.__contains__(name):
            raise ValueError('There is already a variable declared with the name: ' + name)

        self.stack[name] = self.dataInStack
        self.dataInStack += 1
        return Data(name, self.dataInStack - 1, Location.STACK)

    def findDataLocation(self, name):
        stack_value = self.stack.get(name, None)

        if stack_value is not None:
            return Data(name, stack_value, Location.STACK)
        else:
            return self.parent.findDataLocation(name)
