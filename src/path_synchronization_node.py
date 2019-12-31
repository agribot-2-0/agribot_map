#!/usr/bin/env python
import rospy
import firebase_admin
from firebase_admin import credentials, storage
import rospkg
import sys
from os import path
from lxml import etree
import xml.etree.ElementTree as ET
import re
import math
from matplotlib import pyplot as plt
import numpy as np
import yaml

def filter_points(latitude, longitude, step):
    for i in range(0,3):
        del latitude[step-1::step]
        del longitude[step-1::step]

def get_pose(latitude, longitude, ind):
    return dict(pose=dict(position=[float(latitude[ind][0]),float(longitude[ind][0]),0.0],orientation=[0.0,0.0,0.0,1.0]))

def save_to_yaml(latitude, longitude, name):
    for i in range(0, len(latitude)):
        with open(name+'.yaml', 'a') as file:
            yaml.dump(get_pose(latitude, longitude, i), file)

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
    
    #find all files inside user folder:
    blobs_names = list(filter(lambda k: user_id in k, blobs_names))
    
    if(len(blobs_names) < 1):
        rospy.logerr("[Path synchronization node] User folder does not exists")
        #TODO ???: create folder for user_id

    #find all paths with given name insde user folder:
    blobs_names = list(filter(lambda k: path_name in k, blobs_names))
    path_blob = bucket.blob(blobs_names[0]) #TODO: if more than more path found, check version and select newest
    
    #download path from server and parse it to pykml object
    tree = ET.fromstring(path_blob.download_as_string())
    lineStrings = tree.findall('.//{http://www.opengis.net/kml/2.2}LineString')
    for attributes in lineStrings:
        for subAttribute in attributes:
            if subAttribute.tag == '{http://www.opengis.net/kml/2.2}coordinates':
                path_points = re.split(',| ', subAttribute.text)
                del path_points[:2]

    lon = [path_points[3*i:3*i+1] for i in range(0,math.ceil(len(path_points)/3))]
    lat = [path_points[3*i+1:3*i+2] for i in range(0,math.ceil(len(path_points)/3))]

    lon = list(np.float_(lon))
    lat = list(np.float_(lat))
    filter_points(lon, lat, 2)
    plt.plot(lon, lat, 'r.')
    save_to_yaml(lon, lat, path_name)
    plt.show()

    rospy.spin()

if __name__ == '__main__':
    node()
