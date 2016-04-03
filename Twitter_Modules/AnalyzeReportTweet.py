import json
import os
import re
import requests


class TweetReportAnalyzer:
    def __init__(self):
        self.list_of_words = ['balacera', 'robo', 'asalto']
        self.words_re = re.compile("|".join(self.list_of_words))

    def analyze_tweet_for_keywords(self, tweet):
        if self.words_re.search(tweet):
            return True
        else:
            return False

    def get_location(self, tweet):
        location = self.parse_tweet(tweet)
        r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + location + '&key=' +
                         os.environ['MAPS_API_KEY'])
        json_string = json.dumps(r.json())
        json_string = json.loads(json_string)
        if json_string['status'] == 'OK':
            lat_long_object = json_string['results'][0]['geometry']['location']
            print lat_long_object
            return lat_long_object
        else:
            return False

    @staticmethod
    def parse_tweet(tweet):
        m = re.search('(?P<evento>[^$]+)\s(en)?\s(?P<lugar>[^$]+)$', tweet)
        if m is not None:
            if m.group('evento'):
                if m.group('lugar'):
                    event = m.group('evento')
                    place = m.group('lugar')
                    return place
