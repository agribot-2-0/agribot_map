#!/usr/bin/env python
import os
import threading
import rospy
from agribot_map.task_synchronization.task_class import TaskSync

LOG_TAG = "TaskSynchronizationNode"


def get_param(param_name):
    if not rospy.has_param(param_name):
        raise ValueError("[{}] '{}' param not set".format(LOG_TAG, param_name))
    return rospy.get_param(param_name)


def node():  # pylint: disable=too-many-return-statements, too-many-branches
    rospy.init_node('task_node')
    try:
        rsn = get_param('rsn')
        certificate_file = get_param('certificate_file')
        certificate_path = get_param('certificate_path')
        agribot_map_tasks_path = os.path.join(
            os.environ.get('AGRIBOT_HOME'),
            get_param('agribot_map_tasks_path'))
    except ValueError as exception_msg:
        rospy.logerr(exception_msg)
        return

    # init task handling object:
    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    if not os.path.exists(key_path):
        rospy.logerr("[{}] Key folder not present".format(LOG_TAG))
        return

    task_sync = TaskSync(rsn, agribot_map_tasks_path, threading.Event())
    ret = task_sync.initialize_connection_with_firestore(
        os.path.join(key_path, certificate_file))

    if not ret:
        rospy.logerr(
            "[{}] Bucket does not exist. Initialization failed.".format(
                LOG_TAG))
        return

    # TODO: uncomment to remove all cached tasks and make clean dir
    # shutil.rmtree(agribot_map_tasks_path)
    # os.makedirs(agribot_map_tasks_path)

    # Watch the document
    task_sync.get_doc_ref().on_snapshot(task_sync.firebase_callback)

    rospy.spin()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
