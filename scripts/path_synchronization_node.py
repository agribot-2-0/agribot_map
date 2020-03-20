#!/usr/bin/env python
import sys
from os import path
import rospy
import rospkg
from std_msgs.msg import String
from pathhandler import PathHandler

def node():

    rospy.init_node('path_synchronization_node')
    if len(sys.argv) < 2:
        rospy.logerr("[Path synchronization node] UID not specified.")
        return

    # init path handling object:
    rospack = rospkg.RosPack()
    key_path = rospack.get_path('agribot_map') + "/key/"
    if not path.exists(key_path):
        rospy.logerr("[Path synchronization node] Key folder not present.")
        return

    pathhandle = PathHandler(sys.argv[1], rospack.get_path('agribot_map'))
    ret = pathhandle.initialize_connection_with_firestore(key_path +
                                                          "agribot-cd437-firebase-adminsdk" +
                                                          "-ypr8o-5e1109055d.json")

    if not ret:
        rospy.logerr("[Path synchronization node] Bucket does not exist. Initialization failed.")
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
