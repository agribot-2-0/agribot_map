cmake_minimum_required(VERSION 2.8.3)
project(agribot_map)

find_package(catkin REQUIRED COMPONENTS
  map_server
  rospy
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

install(DIRECTORY launch maps tasks paths osm
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  PATTERN ".svn" EXCLUDE
)

catkin_install_python(PROGRAMS
   scripts/path_synchronization_node.py
   scripts/pathhandler.py
   scripts/task_class.py
   scripts/task_node.py
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
