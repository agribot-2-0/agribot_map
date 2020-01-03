#!/usr/bin/env python
import rospy
import rospkg
import sys
from os import path
from matplotlib import pyplot as plt
import yaml
from pathhandler import PathHandler

def filter_points(latitude, longitude, step):
    for i in range(0,3):
        del latitude[step-1::step]
        del longitude[step-1::step]

def node():
    if (len(sys.argv) < 2):
        rospy.logerr("[Path synchronization node] UID specified.")
        return
    rospack = rospkg.RosPack()
    rospack.list()
    # init path handling object:
    pathhandle = PathHandler(sys.argv[1], rospack.get_path('agribot_map'))
    rospy.init_node('path_synchronization_node')
    key_path = rospack.get_path('agribot_map') + "/key/"
    if(not path.exists(key_path)):
        rospy.logerr("[Path synchronization node] Key folder not present.")
        return
    ret = pathhandle.initialize_connection_with_firestore(key_path + "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
    if(not ret):
        rospy.logerr("[Path synchronization node] Bucket does not exist. Initialization failed.")
        return
    pathhandle.sync_paths()
    rospy.spin()

if __name__ == '__main__':
    node()

