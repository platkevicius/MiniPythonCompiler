class Data:
    def __init__(self, data, offset, location):
        self.data = data
        self.offset = offset
        self.location = location

        @property
        def offset():
            return self.offset

        @offset.setter
        def offset(value):
            self.type_def = value
