from mi.allocation.Data import Data
from mi.allocation.Location import Location


class DataAllocator:

    def __init__(self, parent, data_in_register, data_in_heap):
        self.parent = parent
        self.dataInRegister = data_in_register
        self.dataInHeap = data_in_heap
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
        elif self.parent is not None:
            return self.parent.findDataLocation(name)
        else:
            raise NameError('There is no Variable with name: ' + name + '.')
