from nodes.baseNode import BaseNode
from models.config.properties.actions.template import Template
from models.config.properties.actions.twitter_credentials import TwitterConfigModel
import tweepy


class Tweet(BaseNode):
    credentials = None
    event = None
    template = None

    def transform(self):
        _credentials = TwitterConfigModel(self.step["credentials"])
        _credentials.transform()
        if _credentials.isValid():
            self.credentials = _credentials
        self.event = self.step["event"]
        _template = Template(self.step["template"])
        _template.transform()
        _template.render(self.event)
        if _template.isValid():
            self.template = _template
        print(self.step)

    def isValid(self) -> bool:
        if self.credentials is None or \
                self.template is None or \
                self.event is None:
            return False
        return True

    def execute(self):
        tweet = self.template.render(self.event)
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(self.credentials.api_key, self.credentials.api_key_secret)
        auth.set_access_token(self.credentials.access_token, self.credentials.access_token_secret)

        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        api.update_status(tweet)
