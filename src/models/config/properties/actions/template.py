from models.config.baseConfigModel import BaseConfigModel


class Template(BaseConfigModel):
    template = None
    rendered = ""

    def transform(self):
        self.template = self.raw
    
    def render(self, events) -> str:
        if self.rendered == "":
            self.rendered = self.template
        # Get data from events
        while "${" in self.rendered:
            start = self.rendered.index("${")
            end = self.rendered[start:].index("}") + start + 1
            key = self.rendered[start + 2: end - 1]
            replaced_key = str(self.replaceKey(events, key))
            self.rendered = self.rendered[:start] + replaced_key + self.rendered[end:]
        # Math fix data
        while "$[" in self.rendered:
            start = self.rendered.index("$[")
            end = self.rendered[start:].index("]") + start + 1
            key = self.rendered[start + 2: end - 1]
            replaced_key = str(self.replaceMathOp(key))
            self.rendered = self.rendered[:start] + replaced_key + self.rendered[end:]
        return self.rendered

    def replaceKey(self, events, key):
        if "." in key:
            idx = key.index(".")
            k = key[:idx]
            v = key[idx + 1:]
            if k.isnumeric():
                k = int(k)
            return self.replaceKey(events[k], v)
        else:
            return events[key]

    def replaceMathOp(self, key):
        if "/" in key:
            nums = [int(x) for x in key.split("/")]
            return nums[0] / nums[1]
        if "*" in key:
            nums = [int(x) for x in key.split("*")]
            return nums[0] * nums[1]
        if "-" in key:
            nums = [int(x) for x in key.split("-")]
            return nums[0] - nums[1]
        if "+" in key:
            nums = [int(x) for x in key.split("+")]
            return nums[0] + nums[1]


    def isValid(self) -> bool:
        if self.template is None :
            return False
        return True
