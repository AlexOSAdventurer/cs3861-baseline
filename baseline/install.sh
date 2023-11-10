#!/bin/bash

echo "=========================="
echo "Installing App Baseline"

# Here is where we perform installation of scripts, services, etc.
echo " - Installing ROS packages..."

LIBPANDA_SRC=$(cat /etc/libpanda.d/libpanda_src_dir)
LIBPANDA_USER=$(cat /etc/libpanda.d/libpanda_usr)
LAUNCH_FILE=baseline.launch

source /home/$LIBPANDA_USER/.bashrc

runuser -l $LIBPANDA_USER -c /etc/libpanda.d/apps/baseline/installRosPackages.sh

echo "Installing Baseline demo..."
# runuser -l $LIBPANDA_USER -c /etc/libpanda.d/apps/vsl/installMidVslController.sh
pushd /home/$LIBPANDA_USER/catkin_ws
runuser -l $LIBPANDA_USER -c 'source /opt/ros/noetic/setup.bash && cd catkin_ws && catkin_make'
source devel/setup.sh
rosrun robot_upstart install "cs3861-baseline/launch/${LAUNCH_FILE}" --user root

echo "Enabling can_to_ros startup script"
sudo systemctl daemon-reload
sudo systemctl enable baseline
popd
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
