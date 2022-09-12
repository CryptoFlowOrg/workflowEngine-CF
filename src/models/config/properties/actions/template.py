from models.config.baseConfigModel import BaseConfigModel


def isNumericEnhanced(s: str) -> bool:
    if s.isnumeric():
        return True
    if s[0] == "-" and s[1:].isnumeric():
        return True
    return False


class Template(BaseConfigModel):
    template = None
    rendered = ""

    def transform(self):
        self.template = self.raw

    def render(self, event) -> str:
        if self.rendered == "":
            self.rendered = self.template
        # Get data from event
        while "${" in self.rendered:
            start = self.rendered.index("${")
            end = self.rendered[start:].index("}") + start + 1
            key = self.rendered[start + 2: end - 1]
            replaced_key = str(self.replaceKey(event, key))
            self.rendered = self.rendered[:start] + replaced_key + self.rendered[end:]
        # Math fix data
        while "$[" in self.rendered:
            start = self.rendered.index("$[")
            end = self.rendered[start:].index("]") + start + 1
            key = self.rendered[start + 2: end - 1]
            replaced_key = str(self.replaceMathOp(key))
            self.rendered = self.rendered[:start] + replaced_key + self.rendered[end:]
        return self.rendered

    def replaceKey(self, event, key):
        if "." in key:
            idx = key.index(".")
            k = key[:idx]
            v = key[idx + 1:]
            if isNumericEnhanced(k):
                k = int(k)
            return self.replaceKey(event[k], v)
        else:
            value = event[key]
            if value is None:
                return "" 
            return value

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
        if self.template is None:
            return False
        return True
