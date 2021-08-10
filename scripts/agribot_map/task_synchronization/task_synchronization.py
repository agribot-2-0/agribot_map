import os
import threading
import yaml
from agribot_common.database.firestore import Firestore
from .set_yaml_fields import set_rfid, set_path_name


class TaskSynchronization(object):
    def __init__(self, robot_serial_number, tasks_path, certificate_file):
        self.task_collection_path = u"robots/{}/tasks".format(robot_serial_number)
        self.callback_done = threading.Event()
        self.tasks_path = tasks_path
        self.firestore = Firestore(certificate_file)
        self.uids = self.firestore.get_uids_for_rsn(robot_serial_number)
        self.user_id = self.uids[-1]

    def run(self):
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

    def set_tool(self, tool_name):
        if tool_name == "*":
            tool = dict(angle=0,
                        height=0,
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
            tool = dict(angle=doc_tool.to_dict()['tpl_up_down'],
                        height=doc_tool.to_dict()['tpl_push_pull'],
                        red_valve_flow=doc_tool.to_dict()['yellow'],
                        green_valve_flow=doc_tool.to_dict()['green'],
                        blue_valve_flow=doc_tool.to_dict()['blue'],
                        pto_rpm=doc_tool.to_dict()['pto'],
                        rfid=set_rfid(doc_tool),
                        v_max=doc_tool.to_dict()['v_max'])
        return tool

    def write_yaml(self, doc):
        file_name = self.get_file_path(doc)
        front_tool = self.set_tool(doc.to_dict()['front_tool_name'])
        back_tool = self.set_tool(doc.to_dict()['back_tool_name'])

        dict_to_write = dict(
            task=dict(path_name=[set_path_name(doc)], tpl=dict(front=front_tool, back=back_tool)))

        with open(file_name, 'w') as outfile:
            yaml.dump(dict_to_write, outfile, default_flow_style=False)

    def delete_yaml(self, doc):
        file_name = self.get_file_path(doc)
        os.remove(file_name)

    def get_file_path(self, doc):
        doc_file_name = doc.id + '.yaml'
        file_name = os.path.join(self.tasks_path, doc_file_name)
        return file_name
