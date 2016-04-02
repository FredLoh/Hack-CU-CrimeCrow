import json
import time
import os
import re
from AnalyzeReportTweet import TweetReportAnalyzer
from Twitter_Modules.FirebaseInteraction import FirebaseInteraction
from tweepy import API, TweepError
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


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
        self.reportaje_re = re.compile("|".join(['@reportajereal']))
        self.last_id = '1'
        self.firebase = FirebaseInteraction()
        self.tweet_analyzer = TweetReportAnalyzer()

    def on_status(self, status):
        status.text = self.lowercase_tweets(status.text)
        if self.analyze_if_tweet_is_at_us(status.text):
            # DO STUFF WITH TWEET AT US
            print 'Tweet at us.'
            print status.text
            if self.tweet_analyzer.analyze_tweet_for_keywords(tweet=status.text):
                self.firebase.post_new_report(tweet_id=status.id, tweet=status.text, title='wut')
                try:
                    self.tweet(status.text)
                except TweepError:
                    print 'Duplicate'
        else:
            if self.analyze_tweet_for_keywords(status.text):
                print status.text
                self.firebase.post_new_tweet(tweet_id=status.id, tweet=status.text, title='wut')
                if status.coordinates:
                    print 'coords:', status.coordinates
                if status.place:
                    print 'place:', status.place.full_name

    @staticmethod
    def on_error(status_code):
        print status_code
        return False

    def tweet(self, tweet):
        self.api.update_status(tweet)

    def start_stream(self):
        stream = Stream(self.auth, self)
        stream.filter(track=['balacera', '@ReportajeReal'], async=False)

    @staticmethod
    def lowercase_tweets(tweet):
        return tweet.lower()

    def analyze_tweet_for_keywords(self, tweet):
        if self.words_re.search(tweet):
            return True
        else:
            return False

    def analyze_if_tweet_is_at_us(self, tweet):
        if self.reportaje_re.search(tweet):
            return True
        else:
            return False

    def get_home_timeline(self):
        tweet = self.api.user_timeline(id='709091333969870851', count=1, include_rts=True)
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
        print json_string["user"]["id"]
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
t.start_stream()
