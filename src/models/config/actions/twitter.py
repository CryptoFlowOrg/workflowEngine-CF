from models.config.baseConfigModel import BaseConfigModel


class TwitterConfigModel(BaseConfigModel):
    consumer_key = None
    consumer_secret = None
    access_token = None
    access_token_secret = None
    template = None

    def transform(self):
        self.consumer_key = self.raw["consumer_key"]
        self.consumer_secret = self.raw["consumer_secret"]
        self.access_token = self.raw["access_token"]
        self.access_token_secret = self.raw["access_token_secret"]
        self.template = self.raw["template"]

    def isValid(self) -> bool:
        if self.consumer_key is None or \
                self.consumer_secret is None or \
                self.access_token is None or \
                self.access_token_secret is None or \
                self.template is None:
            return False
        return True
