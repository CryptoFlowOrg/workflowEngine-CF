class BaseConfigModel:
    def __init__(self, raw):
        self.raw = raw

    def transform(self):
        raise Exception(f"Transformation has not been built for model {self.raw}")

    def isValid(self):
        raise Exception(f"Testing has not been built for model {self.raw}")
