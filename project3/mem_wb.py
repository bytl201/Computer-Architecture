class MemWb():
    def __init__(self):
        # data to store
        self.data = None

        # rt or rd
        self.dest = None

        # control signal
        self.mem_to_reg = None

    def reset(self):
        # data to store
        self.data = None

        # rt or rd
        self.dest = None
    
        # control signal
        self.mem_to_reg = None

    def set(self, data: int | None, dest: int | None, mem_to_reg: int | None):
        # data to store
        self.data = data

        # rt or rd
        self.dest = dest

        # control signal
        self.mem_to_reg = mem_to_reg

    def get(self):
        return [self.data, self.dest, self.mem_to_reg]