import os
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API


class DataStream(StreamListener):
    def __init__(self):
        super(DataStream, self).__init__()
        self.consumer_key = os.environ['TWITTER_APP_KEY_0']
        self.consumer_secret = os.environ['TWITTER_APP_SECRET_0']
        self.oauth_key = os.environ['TWITTER_OAUTH_TOKEN_0']
        self.oauth_secret = os.environ['TWITTER_OAUTH_TOKEN_SECRET_0']
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.oauth_key, self.oauth_secret)
        self.api = API(self.auth)

    @staticmethod
    def on_status(status):
        print(status.text)

    @staticmethod
    def on_error(status_code):
        print status_code
        return False

    def start_stream(self):
        stream = Stream(self.auth, self)
        stream.filter(track=['balacera, violencia'], async=False)


t = DataStream()
t.start_stream()
