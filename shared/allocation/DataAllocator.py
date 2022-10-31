from shared.allocation.Data import Data
from shared.allocation.Location import Location
from shared.struct.Struct import Struct


class DataAllocator:

    def __init__(self, parent, data_in_register, data_in_stack, data_in_heap):
        self.parent = parent
        self.dataInRegister = data_in_register
        self.dataInStack = data_in_stack
        self.dataInHeap = data_in_heap
        self.register = {}
        self.stack = {}
        self.heap = {}

    def addData(self, data):
        if self.register.__contains__(data.name) or self.stack.__contains__(data.name) or self.heap.__contains__(data.name):
            raise ValueError('There is already declaration with the name: ' + data.name)

        if type(data) is Struct:
            struct = Data(data, self.dataInHeap, Location.HEAP)
            self.heap[data.name] = struct
            self.dataInHeap += 1
            return struct
        else:
            if self.dataInRegister != 12:
                var = Data(data, self.dataInRegister, Location.REGISTER)
                self.register[data.name] = var
                self.dataInRegister += 1
                return var
            else:
                var = Data(data, self.dataInStack, Location.STACK)
                self.stack[data.name] = var
                self.dataInStack += 1
                return var

    def findData(self, name):
        register_data = self.register.get(name, None)
        stack_data = self.stack.get(name, None)
        heap_data = self.heap.get(name, None)

        if register_data is not None:
            return register_data
        elif stack_data is not None:
            offset = 1
            if self.parent is not None:
                offset = self.parent.dataInStack

            stack_data.offset = offset + stack_data.offset
            return stack_data
        elif heap_data is not None:
            offset = 1
            if self.parent is not None:
                offset = self.parent.dataInHeap

            heap_data.offset = offset + heap_data.offset
            return heap_data
        elif self.parent is not None:
            return self.parent.findData(name)
        else:
            raise NameError('There is no Variable with name: ' + name + '.')

    def getDataInStack(self):
        if self.parent is None:
            return self.dataInStack
        else:
            return self.dataInStack - self.parent.dataInStack
