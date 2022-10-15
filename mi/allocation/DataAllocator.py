from mi.allocation.Data import Data
from mi.allocation.Location import Location


class DataAllocator:

    def __init__(self):
        self.dataInRegister = 0
        self.dataInHeap = 0
        self.register = {}
        self.heap = {}

    def addData(self, name):
        if self.register.__contains__(name) or self.heap.__contains__(name):
            raise ValueError('There is already a variable declared with the name: ' + name)

        if self.dataInRegister != 13:
            self.register[name] = self.dataInRegister
            self.dataInRegister += 1
            return Data(name, self.dataInRegister - 1, Location.REGISTER)
        else:
            self.heap[name] = self.dataInHeap
            self.dataInHeap += 1
            return Data(name, self.dataInHeap - 1, Location.HEAP)

    def findDataLocation(self, name):
        register_value = self.register.get(name, None)
        heap_value = self.heap.get(name, None)

        if register_value is not None:
            return Data(name, register_value, Location.REGISTER)
        elif heap_value is not None:
            return Data(name, heap_value, Location.HEAP)
        else:
            raise NameError('There is no Variable with name: ' + name + '.')
