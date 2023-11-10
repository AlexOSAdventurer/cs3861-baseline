#!/bin/bash
# Author: Matt Nice,Matt Bunting,Alex Richardson

LAUNCH_FILE=baseline.launch

echo "----------------------------"
if [[ $EUID == 0 ]];
  then echo "Do NOT run this script as root"
  exit
fi

source ~/.bashrc

pushd ~/catkin_ws
source devel/setup.sh

# rosrun robot_upstart install can_to_ros/launch/${LAUNCH_FILE} --user root
rosrun robot_upstart install ${LAUNCH_FILE} --user root

echo "Enabling can_to_ros startup script"
sudo systemctl daemon-reload
sudo systemctl enable baseline
popd

echo "----------------------------"
