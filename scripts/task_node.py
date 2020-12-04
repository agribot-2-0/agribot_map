#!/usr/bin/env python
import os
import threading
import shutil
import yaml
import rospy
import rospkg
from task_class import TaskSync

# Create an Event for notifying main thread.
CALLBACK_DONE = threading.Event()
TASKS_PATH = rospkg.RosPack().get_path('agribot_map') + "/tasks/"


# Create a callback on_snapshot function to capture changes
def firebase_callback(doc_snapshot, changes, read_time):  # pylint: disable=unused-argument
    for change in changes:
        if change.type.name == 'ADDED':
            write_yaml(change.document)
        elif change.type.name == 'MODIFIED':
            write_yaml(change.document)
    CALLBACK_DONE.set()


def write_yaml(doc):
    file_name = TASKS_PATH + doc.id + '.yaml'
    dict_to_write = dict(task=dict(
        path_name=[doc.to_dict()['path_name'].encode('ascii', 'ignore')]))
    with open(file_name, 'w') as outfile:
        yaml.dump(dict_to_write, outfile, default_flow_style=False)


def if_param_exists(param_name):
    if not rospy.has_param(param_name):
        rospy.logerr(
            "[AgribotTaskSupervisor] '{}' param not set".format(param_name))
        return False
    return True


def node():  # pylint: disable=too-many-return-statements, too-many-branches
    rospy.init_node('task_node')
    if if_param_exists('rsn'):
        rsn = rospy.get_param('rsn')
    else:
        return

    if if_param_exists('certificate_repo'):
        certificate_repo = rospy.get_param('certificate_repo')
    else:
        return

    if if_param_exists('certificate_file'):
        certificate_file = rospy.get_param('certificate_file')
    else:
        return

    # init task handling object:
    rospack = rospkg.RosPack()
    key_path = os.path.join(rospack.get_path(certificate_repo), "key")
    if not os.path.exists(key_path):
        rospy.logerr("[TaskNode] Key folder not present.")
        return

    task_sync = TaskSync(rsn)
    ret = task_sync.initialize_connection_with_firestore(
        os.path.join(key_path, certificate_file))

    if not ret:
        rospy.logerr(
            "[TaskNode] Bucket does not exist. Initialization failed.")
        return

    # Remove all cached tasks and make clean dir
    shutil.rmtree(TASKS_PATH)
    os.makedirs(TASKS_PATH)

    # Watch the document
    task_sync.get_doc_ref().on_snapshot(firebase_callback)

    rospy.spin()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
