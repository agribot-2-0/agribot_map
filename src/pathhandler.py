import rospy
import firebase_admin
from firebase_admin import credentials, storage
import rospkg
import sys
import os
from lxml import etree
import xml.etree.ElementTree as ET
import re
import math
from matplotlib import pyplot as plt
import numpy as np
import yaml

class PathHandler:
    BUCKET_NAME = 'agribot-cd437.appspot.com'
    PACK_PATH= ""
    user_id = ""
    paths = dict() # index=path_name, value=path_version

    def __init__(self, user_id, pack_path):
        self.user_id = user_id
        self.PACK_PATH = pack_path
        try:
            with open(self.PACK_PATH + "/paths_ver.yaml") as f:
                self.paths = dict(yaml.safe_load(f))
        except IOError:
            f = open(self.PACK_PATH + "/paths_ver.yaml", "w")
        f.close()

    def initialize_connection_with_firestore(self, certificate_file):
        cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(cred)
        self.bucket = storage.bucket(self.BUCKET_NAME)
        if (not self.bucket.exists()):
            return False
        return True

    def get_pose(self, latitude, longitude, ind):
        return dict(pose=dict(position=[float(latitude[ind][0]),float(longitude[ind][0]),0.0],orientation=[0.0,0.0,0.0,1.0]))

    def save_to_yaml(self, latitude, longitude, name):
        if not os.path.exists(self.PACK_PATH + "/paths"):
            os.makedirs(self.PACK_PATH + "/paths")
        for i in range(0, len(latitude)):
            with open(self.PACK_PATH + "/paths/" + name + '.yaml', 'a') as file:
                yaml.dump(self.get_pose(latitude, longitude, i), file)

    def download_path(self, blob_name, path_nam):
        blob_name = self.bucket.blob(blob_name)
        #download path from server and parse it to pykml object
        tree = ET.fromstring(blob_name.download_as_string())
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
        self.save_to_yaml(lon, lat, path_nam)

    def sync_paths(self):
        blobs_names = []
        [blobs_names.append(blobs.name) for blobs in self.bucket.list_blobs()]
        #find all files inside user folder:
        blobs_names = list(filter(lambda k: self.user_id in k, blobs_names))
        if(len(blobs_names) < 1):
            #TODO ???: create folder for user_id
            print("[Path synchronization node] User folder does not exists")
            return
        # #find all paths insde user folder:
        blobs_names = list(filter(lambda k: self.user_id in k, blobs_names))
        #delete first element, because it is user folder name
        del blobs_names[0]
        for blob in blobs_names:
            path_nam = blob[len(self.user_id)+1:len(blob)].split("_v")[0]
            path_ver = int((blob[len(self.user_id)+1:len(blob)].split("_v")[1])[:-4])
            if(path_nam in self.paths):
                #update path version
                if(self.paths[path_nam] < path_ver):
                    print("New path found")
                    self.paths[path_nam] = path_ver
                    self.download_path(blob, path_nam)
            else:
                self.paths[path_nam] = path_ver
                self.download_path(blob, path_nam)
        try:
            with open(self.PACK_PATH + "/paths_ver.yaml", "w") as f:
                yaml.dump(self.paths,f)
        except IOError:
            print("Error opening YAML file.")

