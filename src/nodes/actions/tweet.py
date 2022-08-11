from nodes.baseNode import BaseNode


class Tweet(BaseNode):
    def transform(self):
        print(self.step)

    def execute(self):
        print(self.step)
