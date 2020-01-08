#!/usr/bin/env python
import rospy
import rospkg
from std_msgs.msg import String
import sys
from os import path
from pathhandler import PathHandler

def node():
    if (len(sys.argv) < 2):
        rospy.logerr("[Path synchronization node] UID not specified.")
        return

    pub = rospy.Publisher('agribot/path_sync', String, queue_size=10)

    # init path handling object:
    rospack = rospkg.RosPack()
    pathhandle = PathHandler(sys.argv[1], rospack.get_path('agribot_map'))
    key_path = rospack.get_path('agribot_map') + "/key/"
    if(not path.exists(key_path)):
        rospy.logerr("[Path synchronization node] Key folder not present.")
        return

    ret = pathhandle.initialize_connection_with_firestore(key_path + "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
    if(not ret):
        rospy.logerr("[Path synchronization node] Bucket does not exist. Initialization failed.")
        return

    rospy.init_node('path_synchronization_node')

    rate = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        if (pathhandle.sync_paths()):
                pub.publish("New path availible")
        rate.sleep()

if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
