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
