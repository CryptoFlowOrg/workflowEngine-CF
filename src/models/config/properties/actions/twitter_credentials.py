from models.config.baseConfigModel import BaseConfigModel


class TwitterConfigModel(BaseConfigModel):
    api_key = None
    api_key_secret = None
    bearer_token = None
    access_token = None
    access_token_secret = None
    client_id = None
    client_secret = None

    def transform(self):
        self.api_key = self.raw["api_key"]
        self.api_key_secret = self.raw["api_key_secret"]
        self.bearer_token = self.raw["bearer_token"]
        self.access_token = self.raw["access_token"]
        self.access_token_secret = self.raw["access_token_secret"]
        self.client_id = self.raw["client_id"]
        self.client_secret = self.raw["client_secret"]

    def isValid(self) -> bool:
        if self.api_key is None or \
                self.api_key_secret is None or \
                self.bearer_token is None or \
                self.access_token is None or \
                self.access_token_secret is None or \
                self.client_id is None or \
                self.client_secret is None:
            return False
        return True
