import re


class TweetReportAnalyzer:
    def __init__(self):
        self.list_of_words = ['balacera', 'robo', 'asalto']
        self.words_re = re.compile("|".join(self.list_of_words))

    def analyze_tweet_for_keywords(self, tweet):
        if self.words_re.search(tweet):
            return True
        else:
            return False
