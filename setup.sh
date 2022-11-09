#!/bin/bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-get install -y curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

sudo apt-get update
sudo apt-get -y install ros-melodic-desktop
sudo apt-get -y install ros-melodic-tf2-geometry-msgs ros-melodic-ackermann-msgs ros-melodic-joy ros-melodic-map-server ros-melodic-usb-cam ros-melodic-web-video-server ros-melodic-rosbridge-server 
sudo apt-get -y install python-catkin-tools python3-dev python3-numpy python-pip python3-pip
sudo apt-get -y install  i2c-tools libi2c-dev

pip3 install rospkg catkin_pkg empy  requests paho-mqtt
pip2 install  requests paho-mqtt

sudo ln -s /usr/include/opencv4 /usr/include/opencv || true

git clone --branch main https://github.com/eclipse-muto/messages.git  src/messages
git clone --branch main  https://github.com/eclipse-muto/core.git   src/core
git clone --branch main  https://github.com/eclipse-muto/agent.git   src/agent
git clone --branch main  https://github.com/eclipse-muto/composer.git   src/composer

find /src -type f -iname "*.py" -exec chmod +x {} \;

export ROS_PYTHON_VERSION=3

ROS_PYTHON_VERSION=3 source /opt/ros/melodic/setup.bash && catkin_make
