import firebase_admin
from firebase_admin import credentials, storage
import os
import xml.etree.ElementTree as ET
import re
import math
import numpy as np
import yaml

class PathHandler:
    KML_LINE_STRING = './/{http://www.opengis.net/kml/2.2}LineString'
    KML_COORD = '{http://www.opengis.net/kml/2.2}coordinates'

    BUCKET_NAME = 'agribot-cd437.appspot.com'
    PACK_PATH= ""
    PATH_VER_PATH = ""
    user_id = ""
    paths = dict() # index=path_name, value=path_version

    def __init__(self, user_id, pack_path):
        self.user_id = user_id
        self.PACK_PATH = pack_path
        self.PATH_VER_PATH = self.PACK_PATH + "/paths_ver.yaml"
        self.PATHS_PATH = self.PACK_PATH + "/paths"
        try:
            with open(self.PATH_VER_PATH) as file:
                self.paths = dict(yaml.safe_load(file))
        except IOError:
            file = open(self.PATH_VER_PATH, "w")
        file.close()


    def filter_points(self, latitude, longitude, step):
        for i in range(0,3):
            del latitude[step-1::step]
            del longitude[step-1::step]

    def extract_lon(self, points):
        return [points[3*i:3*i+1] for i in range(0, math.ceil(len(points)/3))]

    def extract_lat(self, points):
        return [points[3*i+1:3*i+2] for i in range(0, math.ceil(len(points)/3))]

    def get_all_user_paths(self, blob_nam):
        return list(filter(lambda k: self.user_id in k, blob_nam))

    def get_pose(self, latitude, longitude, ind):
        return dict(pose = dict(position = 
        [float(latitude[ind][0]), float(longitude[ind][0]), 0.0], orientation = [0.0, 0.0, 0.0, 1.0]))

    def parse_path_name(self, blb):
        return blb[len(self.user_id)+1:len(blb)].split("_v")[0]
    
    def parse_path_number(self, blb):
        return int((blb[len(self.user_id)+1:len(blb)].split("_v")[1])[:-4])

    def get_all_blobs_from_bucket(self,blb_name):
        [blb_name.append(blobs.name) for blobs in self.bucket.list_blobs()]
        return blb_name

    def get_path_points_from_blob(self, blb_name):
        tree = ET.fromstring(blb_name.download_as_string())
        lineStrings = tree.findall(self.KML_LINE_STRING)
        for attributes in lineStrings:
            for subAttribute in attributes:
                if subAttribute.tag == self.KML_COORD:
                    path_pts = re.split(',| ', subAttribute.text)
                    del path_pts[:2]
        return path_pts

    def get_path_location(self, path_nm):
        return self.PATHS_PATH + "/" + path_nm + ".yaml"

    def initialize_connection_with_firestore(self, certificate_file):
        cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(cred)
        self.bucket = storage.bucket(self.BUCKET_NAME)
        if (not self.bucket.exists()):
            return False
        return True

    def save_to_yaml(self, latitude, longitude, name):
        if not os.path.exists(self.PATHS_PATH):
            os.makedirs(self.PATHS_PATH)
        open(self.get_path_location(name), 'w').close()
        for i in range(0, len(latitude)):
            with open(self.get_path_location(name), 'a') as file:
                yaml.dump(self.get_pose(latitude, longitude, i), file)
        file.close()

    def download_path(self, blob_name, path_nam):
        blob_name = self.bucket.blob(blob_name)
        path_points = self.get_path_points_from_blob(blob_name)
        lon = self.extract_lon(path_points)
        lat = self.extract_lat(path_points)
        lon = list(np.float_(lon))
        lat = list(np.float_(lat))
        self.save_to_yaml(lon, lat, path_nam)

    def sync_paths(self):
        blobs_names = []
        is_new_path_availible = False
        blobs_names = self.get_all_blobs_from_bucket(blobs_names)
        blobs_names = self.get_all_user_paths(blobs_names)
        if(len(blobs_names) < 1):
            print("[Path synchronization node] User folder does not exists")
            return False
        #delete first element, because it is user folder name
        del blobs_names[0]
        for blob in blobs_names:
            path_nam = self.parse_path_name(blob)
            path_ver = self.parse_path_number(blob)
            if(path_nam in self.paths):
                if(self.paths[path_nam] < path_ver):
                    self.paths[path_nam] = path_ver
                    self.download_path(blob, path_nam)
                    is_new_path_availible = True
            else:
                self.paths[path_nam] = path_ver
                self.download_path(blob, path_nam)
                is_new_path_availible = True
        try:
            with open(self.PATH_VER_PATH, "w") as file:
                yaml.dump(self.paths, file)
        except IOError:
            print("Error opening YAML file.")

        return is_new_path_availible
