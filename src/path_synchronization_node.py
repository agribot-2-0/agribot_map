#!/usr/bin/env python
import rospy
import firebase_admin
from firebase_admin import credentials, storage
import rospkg
import sys
from os import path

def node():
    print(len(sys.argv))
    if (len(sys.argv) < 2):
        rospy.logerr("[Path synchronization node] UID not specified.")
        return
    
    rospack = rospkg.RosPack()
    rospack.list()
    pack_path = rospack.get_path('agribot_map') + "/key/"
    if(not path.exists(pack_path)):
        rospy.logerr("[Path synchronization node] Key folder not present.")
        return

    rospy.init_node('path_synchronization_node')    
    cred = credentials.Certificate(pack_path + "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
    firebase_admin.initialize_app(cred)
    bucket = storage.bucket('agribot-cd437.appspot.com')

    if (not bucket.exists()):
        rospy.logerr("[Path synchronization node] Bucket does not exist.")
    
    blobs = list(bucket.list_blobs())
    [print(blobs.name) for blobs in blobs]

    rospy.spin()

if __name__ == '__main__':
    node()
