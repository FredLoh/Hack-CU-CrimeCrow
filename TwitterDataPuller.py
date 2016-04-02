import time
import os
import re
import json
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
        self.last_id = '1'

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
        stream.filter(track=['balacera'], async=True)

    @staticmethod
    def lowercase_tweets(tweet):
        return tweet.lower()

    def analyze_tweet_for_keywords(self, tweet):
        if self.words_re.search(tweet):
            print tweet

    def get_home_timeline(self):
        tweet = self.api.user_timeline(screen_name='ReportajeReal', count=1, include_rts=True)
        tweet_id = self.get_id_from_tweet_status_object(tweet)
        if self.check_last_tweet():
            print 'Found new tweet.'
            self.store_last_tweet_id(str(tweet_id))
            self.sleep_for(30)
        else:
            self.sleep_for(30)

    @staticmethod
    def get_id_from_tweet_status_object(status):
        status = status[0]
        json_string = json.dumps(status._json)
        json_string = json.loads(json_string)
        print json_string["text"]
        return json_string["id"]

    @staticmethod
    def sleep_for(seconds):
        print 'Sleeping'
        time.sleep(seconds)

    @staticmethod
    def store_last_tweet_id(tweet_id):
        with open("last_id.txt", "w+") as text_file:
            text_file.write(tweet_id)

    def check_last_tweet(self):
        with open("last_id.txt", "r") as text_file:
            for line in text_file:
                if line == self.last_id:
                    return False
                else:
                    return True

t = DataStream()
t.get_home_timeline()
