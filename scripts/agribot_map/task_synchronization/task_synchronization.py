import os
import threading
import yaml
from agribot_common.database.firestore import Firestore
from agribot_map.task_synchronization.set_yaml_fields import get_rfid_from_tool_doc, \
    get_path_name_from_task_doc


class TaskSynchronization(object):
    def __init__(self, robot_serial_number, tasks_path, certificate_file):
        self.task_collection_path = u"robots/{}/tasks".format(robot_serial_number)
        self.callback_done = threading.Event()
        self.tasks_path = tasks_path
        self.firestore = Firestore(certificate_file)
        self.uids = self.firestore.get_uids_for_rsn(robot_serial_number)
        # TODO(all): Add path synchronization for many assigned users
        # right now take one user from all assigned users
        self.user_id = self.uids[-1]
        self.tool_collection_path = u"users/{}/tools".format(self.user_id)

    def run(self):
        self.firestore.register_callback_on_collection_change(self.tool_collection_path,
                                                              self.firebase_tool_callback)
        self.firestore.register_callback_on_collection_change(self.task_collection_path,
                                                              self.firebase_task_callback)

    def firebase_task_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument
        for change in changes:
            if change.type.name == 'ADDED':
                self.write_yaml(change.document)
            elif change.type.name == 'MODIFIED':
                self.write_yaml(change.document)
            elif change.type.name == 'REMOVED':
                self.delete_yaml(change.document)
        self.callback_done.set()

    def firebase_tool_callback(self, doc_snapshot, changes, read_time):  # pylint: disable=unused-argument
        for change in changes:
            if change.type.name == 'ADDED':
                self.update_tools_in_tasks(change.document.id)
            elif change.type.name == 'MODIFIED':
                self.update_tools_in_tasks(change.document.id)
            #elif change.type.name == 'REMOVED':
            #TODO(all): think how to handle removed tools

        self.callback_done.set()

    def update_tools_in_tasks(self, tool_name):
        docs_front = list(
            self.firestore.database.collection(self.task_collection_path).where(
                u'front_tool_name', u'==', tool_name).stream())
        docs_back = list(
            self.firestore.database.collection(self.task_collection_path).where(
                u'back_tool_name', u'==', tool_name).stream())
        docs = list(set(docs_front + docs_back))
        for doc in docs:
            self.write_yaml(doc)

    def set_tool(self, tool_name):
        if tool_name == "*":
            tool = dict(angle=0.8,
                        height=0.05,
                        red_valve_flow=0,
                        green_valve_flow=0,
                        blue_valve_flow=0,
                        pto_rpm=0,
                        rfid=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        v_max=0)
        else:
            doc_tool_ref = self.firestore.database.collection('users').document(
                self.user_id).collection('tools').document(tool_name)
            doc_tool = doc_tool_ref.get()
            tool = dict(angle=float(doc_tool.to_dict()['tpl_up_down']),
                        height=float(doc_tool.to_dict()['tpl_push_pull']),
                        red_valve_flow=int(doc_tool.to_dict()['yellow']),
                        green_valve_flow=int(doc_tool.to_dict()['green']),
                        blue_valve_flow=int(doc_tool.to_dict()['blue']),
                        pto_rpm=int(doc_tool.to_dict()['pto']),
                        rfid=get_rfid_from_tool_doc(doc_tool),
                        v_max=float(doc_tool.to_dict()['v_max']))
        return tool

    def write_yaml(self, doc):
        file_name = self.get_file_path(doc)
        front_tool = self.set_tool(doc.to_dict()['front_tool_name'])
        back_tool = self.set_tool(doc.to_dict()['back_tool_name'])

        dict_to_write = dict(task=dict(path_name=[get_path_name_from_task_doc(doc)],
                                       tpl=dict(front=front_tool, back=back_tool)))

        with open(file_name, 'w') as outfile:
            yaml.dump(dict_to_write, outfile, default_flow_style=False)

    def delete_yaml(self, doc):
        file_name = self.get_file_path(doc)
        os.remove(file_name)

    def get_file_path(self, doc):
        doc_file_name = doc.id + '.yaml'
        file_name = os.path.join(self.tasks_path, doc_file_name)
        return file_name
