class IfId():

    def __init__(self):
        self.instruction = None

    def reset(self):
        self.instruction = None

    def set(self, instruction: int | None):
        self.instruction = instruction

    def get(self):
        return self.instruction