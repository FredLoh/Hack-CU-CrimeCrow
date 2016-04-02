from firebase import firebase


class FirebaseInteraction:
    def __init__(self):
        self.firebase = firebase.FirebaseApplication('https://vmx.firebaseio.com/', None)

    def check_users(self):
        result = self.firebase.get('/users', '1')
        print result

    def get_reports(self):
        result = self.firebase.get('/users', '1')
        print result
