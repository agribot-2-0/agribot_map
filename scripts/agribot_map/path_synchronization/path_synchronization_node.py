#!/usr/bin/env python
import os
import threading
import rospy
from agribot_map.path_synchronization.pathhandler import PathHandler
from agribot_map.task_synchronization.task_class import TaskSync
from google.api_core import exceptions

LOG_TAG = "PathSynchronizationNode"


def get_param(param_name):
    if not rospy.has_param(param_name):
        raise ValueError("[{}] '{}' param not set".format(LOG_TAG, param_name))
    return rospy.get_param(param_name)


def node():  # pylint: disable=too-many-return-statements, too-many-branches, too-many-locals
    rospy.init_node('path_synchronization_node')

    try:
        rsn = get_param('rsn')
        certificate_path = get_param('certificate_path')
        certificate_file = get_param('certificate_file')
        agribot_map_tasks_path = os.path.join(
            os.environ.get('AGRIBOT_HOME'),
            get_param('agribot_map_tasks_path'))
        agribot_map_config_path = os.path.join(
            os.environ.get('AGRIBOT_HOME'),
            get_param('agribot_map_paths_path'))
    except ValueError as exception_msg:
        rospy.logerr(exception_msg)
        return

    # init path handling object:
    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    key_file = os.path.join(key_path, certificate_file)
    if not os.path.exists(key_path):
        rospy.logerr("[{}] Key folder {} not present".format(
            LOG_TAG, key_path))
        return

    task_sync = TaskSync(rsn, agribot_map_tasks_path, threading.Event())
    ret_val = task_sync.initialize_connection_with_firestore(key_file)

    if not ret_val:
        rospy.logerr(
            "[{}] Bucket does not exist. Initialization failed.".format(
                LOG_TAG))
        return

    uids = task_sync.get_uids()

    if not uids:
        rospy.logerr("[{}] Robot is not assigned to any user".format(LOG_TAG))
        return

    pathhandle = PathHandler(uids[-1], agribot_map_config_path)
    try:
        ret = pathhandle.initialize_connection_with_firestore(key_file)
    except exceptions.Forbidden as my_except:
        rospy.logerr("[{}] Exeption: {}".format(LOG_TAG, my_except))
        return
    except exceptions.TooManyRequests as my_except:
        rospy.logerr("[{}] Exeption: {}".format(LOG_TAG, my_except))
        return

    if not ret:
        rospy.logerr(
            "[{}] Bucket does not exist. Initialization failed.".format(
                LOG_TAG))
        return

    rate = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        try:
            path_name = pathhandle.sync_paths()
            if path_name:
                rospy.logwarn("[{}] Download path {}".format(
                    LOG_TAG, path_name))
        except IOError as exception_msg:
            rospy.logerr(exception_msg)

        rate.sleep()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
