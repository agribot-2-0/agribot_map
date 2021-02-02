#!/usr/bin/env python
import os
import rospy
from agribot_common.agribot_parameters import get_parameter
from agribot_common.database.firestore import Firestore
from agribot_map.path_synchronization.pathhandler import PathHandler
from google.api_core import exceptions

LOG_TAG = "PathSynchronizationNode"


def node():
    rospy.init_node('path_synchronization_node')

    try:
        rsn = get_parameter('rsn')
        certificate_path = get_parameter('certificate_path')
        certificate_file = get_parameter('certificate_file')
        agribot_map_config_path = os.path.join(
            os.environ.get('AGRIBOT_HOME'),
            get_parameter('/agribot_map/paths_path'))
    except ValueError as exception_msg:
        rospy.logerr(exception_msg)
        return

    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    key_file = os.path.join(key_path, certificate_file)
    if not os.path.exists(key_path):
        rospy.logerr("[{}] Key folder {} not present".format(
            LOG_TAG, key_path))
        return

    firestore = Firestore(key_file)
    uids = firestore.get_uids_for_rsn(rsn)

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
            pathhandle.sync_paths()
        except IOError as exception_msg:
            rospy.logerr(exception_msg)

        rate.sleep()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
