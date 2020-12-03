#!/usr/bin/env python
import sys
from os import path
import rospy
import rospkg
from std_msgs.msg import String
from pathhandler import PathHandler
from google.api_core import exceptions
from task_class import TaskSync


def node():
    rospy.init_node('path_synchronization_node')
    if not rospy.has_param('rsn'):
        rospy.logerr("[Path synchronization node] rsn param not set")
        return

    rsn = rospy.get_param('rsn')

    # init path handling object:
    rospack = rospkg.RosPack()
    key_path = path.join(rospack.get_path('agribot_map'), "key")
    key_file = path.join(
        key_path, "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
    if not path.exists(key_path):
        rospy.logerr("[Path synchronization node] Key folder not present.")
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
