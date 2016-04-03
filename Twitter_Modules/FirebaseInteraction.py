from firebase import Firebase


class FirebaseInteraction:
    def __init__(self):
        self.tweet_firebase = Firebase('https://vmx.firebaseio.com/tweets')
        self.report_firebase = Firebase('https://vmx.firebaseio.com/reports')

    def post_new_tweet(self, tweet_id, title, tweet, location_title, lat, lon, username):
        if location_title != '':
            response = self.tweet_firebase.push({'username': username, 'tweet_id': tweet_id, 'title': title, 'text': tweet, 'location':
                                                 {'title': location_title, 'lat': lat, 'lon': lon}})
        else:
            response = self.tweet_firebase.push({'username': username, 'tweet_id': tweet_id, 'title': title, 'text': tweet})
        print response

    def post_new_report(self, tweet_id, title, tweet, location_title, lat, lon, username):
        if location_title != '':
            response = self.report_firebase.push({'username': username, 'tweet_id': tweet_id, 'title': title, 'text': tweet, 'location':
                                                 {'title': location_title, 'lat': lat, 'lon': lon}})
        else:
            response = self.report_firebase.push({'username': username, 'tweet_id': tweet_id, 'title': title, 'text': tweet})
        print response
