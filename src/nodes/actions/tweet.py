from nodes.baseNode import BaseNode
from models.config.properties.actions.template import Template
from models.config.properties.actions.twitter_credentials import TwitterConfigModel
import tweepy


class Tweet(BaseNode):
    credentials = None
    condensed_events = []

    
    def transform(self):
        self.credentials = TwitterConfigModel(self.step["credentials"])
        self.credentials.transform()
        self.condensed_events = self.step["condensed_events"]
        self.template = Template(self.step["template"])
        self.template.transform()
        print(self.step)

    def isValid(self) -> bool:
        if not self.credentials.isValid() or \
                not self.template.isValid():
            return False
        return True

    def execute(self):
        tweet = self.template.render(self.condensed_events)
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(self.credentials.api_key, self.credentials.api_key_secret)
        auth.set_access_token(self.credentials.access_token, self.credentials.access_token_secret)

        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        api.update_status(tweet)