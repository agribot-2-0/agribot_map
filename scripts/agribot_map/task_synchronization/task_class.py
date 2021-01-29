import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import yaml


class TaskSync(object):
    def __init__(self, rsn, tasks_path, event):
        self.database = None
        self.rsn = rsn  # robot serial number
        self.callback_done = event
        self.tasks_path = tasks_path

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

    def firebase_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument
        for change in changes:
            if change.type.name == 'ADDED':
                self.write_yaml(change.document)
            elif change.type.name == 'MODIFIED':
                self.write_yaml(change.document)
        self.callback_done.set()

    def write_yaml(self, doc):
        doc_file_name = doc.id + '.yaml'
        file_name = os.path.join(self.tasks_path, doc_file_name)
        dict_to_write = dict(task=dict(
            path_name=[doc.to_dict()['path_name'].encode('ascii', 'ignore')]))
        with open(file_name, 'w') as outfile:
            yaml.dump(dict_to_write, outfile, default_flow_style=False)
