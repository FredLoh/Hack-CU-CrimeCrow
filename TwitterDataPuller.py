import os
import re
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API


class DataStream(StreamListener):
    def __init__(self):
        super(DataStream, self).__init__()
        self.consumer_key = os.environ['HACKCU_APP_KEY']
        self.consumer_secret = os.environ['HACKCU_KEY_SECRET']
        self.oauth_key = os.environ['HACKCU_OAUTH_TOKEN']
        self.oauth_secret = os.environ['HACKCU_OAUTH_SECRET']
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.oauth_key, self.oauth_secret)
        self.api = API(self.auth)
        self.list_of_words = ['en', 'entre', 'calle', 'interior',
                              'carretera', 'rumbo', 'evite']
        self.words_re = re.compile("|".join(self.list_of_words))

    def on_status(self, status):
        status.text = self.lowercase_tweets(status.text)
        print status.text
        self.analyze_tweet_for_keywords(status.text)
        if status.coordinates:
            print 'coords:', status.coordinates
        if status.place:
            print 'place:', status.place.full_name

    @staticmethod
    def on_error(status_code):
        print status_code
        return False

    def start_stream(self):
        stream = Stream(self.auth, self)
        stream.filter(track=['balacera'], async=False)

    @staticmethod
    def lowercase_tweets(tweet):
        return tweet.lower()

    def analyze_tweet_for_keywords(self, tweet):
        if self.words_re.search(tweet):
            print tweet


t = DataStream()
t.start_stream()
