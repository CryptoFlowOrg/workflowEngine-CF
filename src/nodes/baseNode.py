class BaseNode:
    def __init__(self, step):
        self.step = step

    def execute(self):
        raise Exception("step has not been configured")

    def transform(self):
        raise Exception("transformation has not been configured")

    def isValid(self):
        raise Exception(f"Testing has not been built for model {self.raw}")