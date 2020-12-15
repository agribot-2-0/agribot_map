#!/usr/bin/env python
import os
import rospy
import rospkg
from std_msgs.msg import String
from pathhandler import PathHandler
from google.api_core import exceptions
from task_class import TaskSync


def if_param_exists(param_name):
    if not rospy.has_param(param_name):
        rospy.logerr(
            "[AgribotTaskSupervisor] '{}' param not set".format(param_name))
        return False
    else:
        return True


def node():  # pylint: disable=too-many-return-statements, too-many-branches
    rospy.init_node('path_synchronization_node')
    if if_param_exists('rsn'):
        rsn = rospy.get_param('rsn')
    else:
        return

    if if_param_exists('certificate_file'):
        certificate_file = rospy.get_param('certificate_file')
    else:
        return

    if if_param_exists('certificate_path'):
        certificate_path = rospy.get_param('certificate_path')
    else:
        return

    # init path handling object:
    rospack = rospkg.RosPack()
    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    key_file = os.path.join(key_path, certificate_file)
    if not os.path.exists(key_path):
        rospy.logerr(
            "[AgribotTaskSupervisor] Key folder {} not present".format(
                key_path))
        return

    task_sync = TaskSync(rsn)
    ret_val = task_sync.initialize_connection_with_firestore(key_file)

    if not ret_val:
        rospy.logerr(
            "[Path synchronization node] Bucket does not exist. Initialization failed."
        )
        return

    uids = task_sync.get_uids()

    if not uids:
        rospy.logerr(
            "[Path synchronization node] Robot is not assigned to any user")
        return

    pathhandle = PathHandler(uids[-1], rospack.get_path('agribot_map'))
    try:
        ret = pathhandle.initialize_connection_with_firestore(key_file)
    except exceptions.Forbidden as my_except:
        rospy.logerr(
            "[Path synchronization node] Exeption: {}".format(my_except))
        return
    except exceptions.TooManyRequests as my_except:
        rospy.logerr(
            "[Path synchronization node] Exeption: {}".format(my_except))
        return

    if not ret:
        rospy.logerr(
            "[Path synchronization node] Bucket does not exist. Initialization failed."
        )
        return

    pub = rospy.Publisher('agribot/path_sync', String, queue_size=10)

    rate = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        if pathhandle.sync_paths():
            pub.publish("New path available")
        rate.sleep()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
