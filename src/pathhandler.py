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
    paths = dict() #dictionary - index=path_names, value=path_version

    def __init__(self, user_id, path_name, pack_path):
        self.user_id = user_id
        self.path_name = path_name
        self.PACK_PATH = pack_path
        try:
            with open(self.PACK_PATH + "/paths_dir.yaml") as f:
                    print(f.readlines())
                    # Do something with the file
        except IOError:
            print("File not accessible")

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
        print(blobs_names)
