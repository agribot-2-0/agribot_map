import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class TaskSync(object):
    def __init__(self, rsn):
        self.database = None
        self.rsn = rsn  # robot serial number

    def initialize_connection_with_firestore(self, certificate_file):
        if not firebase_admin._apps:  # pylint: disable=protected-access
            cred = credentials.Certificate(certificate_file)
            firebase_admin.initialize_app(cred, {
                'projectID': 'agribot-cd437',
            })
            self.database = firestore.client()
        return True

    def get_doc_ref(self):
        return self.database.collection(u'robots').document(
            self.rsn).collection('tasks')

    def get_uids(self):
        uids = []
        users_ref = self.database.collection(u'users').stream()
        for user in users_ref:
            robots_ref = self.database.collection(u'users').document(
                user.id).collection('robots').stream()
            for robot in robots_ref:
                if robot.id == self.rsn:
                    uids.append(user.id)
        return uids
