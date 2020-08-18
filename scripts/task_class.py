import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class TaskSync(object):
    def __init__(self, rsn):
        self.database = None
        self.rsn = rsn  # robot serial number

    def initialize_connection_with_firestore(self, certificate_file):
        cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(cred, {
            'projectID': 'agrsibot-cd437',
        })
        self.database = firestore.client()
        return True

    def get_doc_ref(self):
        return self.database.collection(u'robots').document(
            self.rsn).collection('tasks')
