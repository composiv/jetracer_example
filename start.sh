#!/bin/bash

export ROS_PYTHON_VERSION=3
ROS_PYTHON_VERSION=3 source /opt/ros/melodic/setup.bash && source devel/setup.bash && roslaunch launch/muto.launch
