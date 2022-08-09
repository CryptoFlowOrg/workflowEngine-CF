class BaseNode:
    def __init__(self, step):
        self.step = step

    def execute(self):
        raise Exception("step has not been configured")