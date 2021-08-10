cmake_minimum_required(VERSION 2.8.3)
project(agribot_map)

find_package(catkin REQUIRED COMPONENTS
  map_server
  rospy
)

catkin_python_setup()

catkin_package()

###########
## Build ##
###########

include_directories(
  ${catkin_INCLUDE_DIRS}
)

#############
## Install ##
#############

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  PATTERN ".svn" EXCLUDE
)

catkin_install_python(PROGRAMS
   scripts/agribot_map/path_synchronization/path_synchronization_node.py
   scripts/agribot_map/task_synchronization/task_node.py
   scripts/agribot_map/task_synchronization/set_yaml_fields.py
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

#############
## Testing ##
#############
