import os
import xml.etree.ElementTree as ET
import re
import math
import numpy as np
import yaml
import firebase_admin
from firebase_admin import credentials, storage

class PathHandler:
    kml_line_string = './/{http://www.opengis.net/kml/2.2}LineString'
    kml_coord = '{http://www.opengis.net/kml/2.2}coordinates'

    bucket_name = 'agribot-cd437.appspot.com'
    ros_pack_path = ""
    path_ver_path = ""
    user_id = ""
    paths = dict() # index=path_name, value=path_version
    position_number = 0

    def __init__(self, user_id, pack_path):
        self.user_id = user_id
        self.ros_pack_path = pack_path
        self.path_ver_path = self.ros_pack_path + "/paths_ver.yaml"
        self.paths_path = self.ros_pack_path + "/paths"

        try:
            with open(self.path_ver_path) as file:
                if os.stat(self.path_ver_path).st_size != 0:
                    self.paths = dict(yaml.safe_load(file))
        except IOError:
            file = open(self.path_ver_path, "w")
        file.close()

    def extract_lon(self, points):
        # points[3*i:3*i+1] is dictated by format of data
        # received from parsing KML file in get_path_points_from_blob method points list
        # like so: [alt1,lon1,lat1,alt1,lon1,lat1,...]
        return list(np.float_([points[3*i:3*i+1] for i in range(0, int(math.ceil(len(points)/3)))]))

    def extract_lat(self, points):
        # points[3*i+1:3*i+2] is dictated by format of data
        # received from parsing KML file in get_path_points_from_blob method points list
        # like so: [alt1,lon1,lat1,alt1,lon1,lat1,...]
        return list(np.float_([points[3*i+1:3*i+2] for i in range(0, int(math.ceil(len(points)/3)))]))

    def get_all_user_paths(self, blob_nam):
        return list(filter(lambda k: self.user_id in k, blob_nam))

    def get_pose(self, latitude, longitude, ind):
        pose = dict()
        pose[("pose" + str(self.position_number))] = dict(position=[float(longitude[ind][0]),
                                                                    float(latitude[ind][0]), 0.0],
                                                          orientation=[0.0, 0.0, 0.0, 1.0])
        self.position_number = self.position_number + 1
        return pose

    def parse_path_name(self, blb):
        return blb[len(self.user_id)+1:len(blb)].split("_v")[0]

    def parse_path_number(self, blb):
        return int((blb[len(self.user_id)+1:len(blb)].split("_v")[1])[:-4])

    def get_all_blobs_from_bucket(self, blb_name):
        [blb_name.append(blobs.name) for blobs in self.bucket.list_blobs()]
        return blb_name

    def get_path_points_from_blob(self, blb_name):
        tree = ET.fromstring(blb_name.download_as_string())
        line_string = tree.findall(self.kml_line_string)
        for attributes in line_string:
            for sub_attribute in attributes:
                if sub_attribute.tag == self.kml_coord:
                    path_pts = re.split(',| ', sub_attribute.text)
                    del path_pts[:2]
        return path_pts

    def get_path_location(self, path_nm):
        return self.paths_path + "/" + path_nm + ".yaml"

    def initialize_connection_with_firestore(self, certificate_file):
        cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(cred)
        self.bucket = storage.bucket(self.bucket_name)
        if not self.bucket.exists():
            return False
        return True

    def save_to_yaml(self, latitude, longitude, name):
        self.position_number = 0
        if not os.path.exists(self.paths_path):
            os.makedirs(self.paths_path)
        open(self.get_path_location(name), 'w').close()
        for i in range(0, len(latitude)):
            with open(self.get_path_location(name), 'a') as file:
                yaml.safe_dump(self.get_pose(latitude, longitude, i), file)
        file.close()

    def download_path(self, blob_name, path_nam):
        blob_name = self.bucket.blob(blob_name)
        path_points = self.get_path_points_from_blob(blob_name)
        lon = self.extract_lon(path_points)
        lat = self.extract_lat(path_points)

        self.save_to_yaml(lon, lat, path_nam)

    def sync_paths(self):
        blobs_names = []
        is_new_path_availible = False

        blobs_names = self.get_all_blobs_from_bucket(blobs_names)
        blobs_names = self.get_all_user_paths(blobs_names)

        if len(blobs_names) < 1:
            print("[Path synchronization node] User folder does not exists")
            return False
        #delete first element, because it is user folder name
        del blobs_names[0]

        for blob in blobs_names:
            path_nam = self.parse_path_name(blob)
            path_ver = self.parse_path_number(blob)
            if path_nam in self.paths:
                if self.paths[path_nam] < path_ver:
                    self.paths[path_nam] = path_ver
                    self.download_path(blob, path_nam)
                    is_new_path_availible = True
            else:
                self.paths[path_nam] = path_ver
                self.download_path(blob, path_nam)
                is_new_path_availible = True
        try:
            with open(self.path_ver_path, "w") as file:
                yaml.safe_dump(self.paths, file)
        except IOError:
            print("Error opening YAML file.")

        return is_new_path_availible
