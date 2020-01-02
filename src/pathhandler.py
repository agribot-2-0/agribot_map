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

class PathHandler:
    BUCKET_NAME = 'agribot-cd437.appspot.com'
    PACK_PATH= ""
    user_id = ""
    path_name = ""
    #paths dictionary - index=path_names, value=path_version

    def __init__(self, user_id, path_name, pack_path):
        self.user_id = user_id
        self.path_name = path_name
        self.PACK_PATH = pack_path
        try:
            with open(self.PACK_PATH + "/paths_ver.yaml") as f:
                self.paths = dict(yaml.safe_load(f))
        except IOError:
            print("Error opening YAML file.")
        f.close()
        
        if(len(self.paths)<=0):
            self.paths = dict()


    def initialize_connection_with_firestore(self, certificate_file):
        cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(cred)
        self.bucket = storage.bucket(self.BUCKET_NAME)
        if (not self.bucket.exists()):
            return False
        return True

    def sync_paths(self):
        blobs_names = []
        [blobs_names.append(blobs.name) for blobs in self.bucket.list_blobs()]
        #find all files inside user folder:
        blobs_names = list(filter(lambda k: self.user_id in k, blobs_names))
        if(len(blobs_names) < 1):
            print("[Path synchronization node] User folder does not exists")
            #TODO ???: create folder for user_id
        #find all paths with given name insde user folder:
        blobs_names = list(filter(lambda k: self.path_name in k, blobs_names))
        #check if every version of path is most current one and update ver file:
        for name in blobs_names:
            path_nam = name[len(self.user_id)+1: len(self.user_id)+len(self.path_name)+1]
            path_version = int(name[len(self.user_id)+len(self.path_name)+3:len(name)-4])
            print(self.paths)
            if(path_nam in self.paths):
                #update path version
                if(self.paths[path_nam] < path_version):
                    print("New path found")
                    self.paths[path_nam] = path_version
            else:
                    self.paths[path_nam] = path_version

        try:
            with open(self.PACK_PATH + "/paths_ver.yaml", "w") as f:
                yaml.dump(self.paths,f)
        except IOError:
            print("Error opening YAML file.")
        
        
