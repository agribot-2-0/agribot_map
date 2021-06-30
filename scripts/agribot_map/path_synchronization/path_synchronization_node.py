#!/usr/bin/env python
import os
import rospy
from agribot_common.agribot_parameters import get_parameter
from agribot_common.database.firestore import Firestore
from agribot_map.path_synchronization.pathhandler import PathHandler
import google.api_core.exceptions

LOG_TAG = "PathSynchronizationNode"


def node():
    rospy.init_node('path_synchronization_node')

    try:
        rsn = get_parameter('rsn')
        certificate_path = get_parameter('certificate_path')
        certificate_file = get_parameter('certificate_file')
        agribot_map_config_path = os.path.join(os.environ.get('AGRIBOT_HOME'),
                                               get_parameter('/agribot_map/paths_path'))
    except ValueError as exception_msg:
        rospy.logerr("[{}] {}".format(LOG_TAG, exception_msg))
        return

    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    key_file = os.path.join(key_path, certificate_file)
    if not os.path.exists(key_path):
        rospy.logerr("[{}] Key folder {} not present".format(LOG_TAG, key_path))
        return

    try:
        firestore = Firestore(key_file)
        uids = firestore.get_uids_for_rsn(rsn)
    except ValueError as exception_msg:
        rospy.logerr("[{}] {}".format(LOG_TAG, exception_msg))
        return

    try:
        # TODO: Add path synchronization for many assigned users
        # right now take one user from all assigned users
        user_id = uids[-1]
        pathhandle = PathHandler(user_id, agribot_map_config_path)
        ret = pathhandle.initialize_connection_with_firestore(key_file)
    except google.api_core.exceptions.GoogleAPIError as my_except:
        rospy.logerr("[{}] Exception: {}".format(LOG_TAG, my_except))
        return
    if not ret:
        rospy.logerr("[{}] Bucket does not exist. Initialization failed.".format(LOG_TAG))
        return

    rate = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        try:
            downloaded_paths = pathhandle.sync_paths()
            if downloaded_paths:
                rospy.logwarn("[{}] New paths downloaded: {}".format(LOG_TAG, downloaded_paths))
        except IOError as exception_msg:
            rospy.logerr("[{}] Exception: {}".format(LOG_TAG, exception_msg))

        rate.sleep()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
