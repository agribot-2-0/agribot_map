#!/usr/bin/env python
import rospy
import firebase_admin
from firebase_admin import credentials, storage
import rospkg
import sys
from os import path

def node():
    #get user ID as argument
    if (len(sys.argv) < 3):
        rospy.logerr("[Path synchronization node] UID not specified.")
        return
    user_id = sys.argv[1]
    path_name = sys.argv[2]

    #get key and authenticate
    rospack = rospkg.RosPack()
    rospack.list()
    pack_path = rospack.get_path('agribot_map') + "/key/"
    if(not path.exists(pack_path)):
        rospy.logerr("[Path synchronization node] Key folder not present.")
        return
    cred = credentials.Certificate(pack_path + "agribot-cd437-firebase-adminsdk-ypr8o-5e1109055d.json")
    firebase_admin.initialize_app(cred)
    bucket = storage.bucket('agribot-cd437.appspot.com')
    if (not bucket.exists()):
        rospy.logerr("[Path synchronization node] Bucket does not exist.")
        return

    #if everythong went well init node
    rospy.init_node('path_synchronization_node')
    blobs_names = []
    [blobs_names.append(blobs.name) for blobs in bucket.list_blobs()]
    
    #filter out files inside user id folder:
    blobs_names = list(filter(lambda k: user_id in k, blobs_names))
    
    print(blobs_names)

    if(len(blobs_names) < 1):
        rospy.logerr("[Path synchronization node] User folder does not exists")
        #TODO ???: create folder for user_id
    
    blobs_names = list(filter(lambda k: path_name in k, blobs_names))
    print(blobs_names)

    path_blob = bucket.blob(blobs_names[0])
    path_blob.download_as_string()
    
    rospy.spin()

if __name__ == '__main__':
    node()
