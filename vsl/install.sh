#!/bin/bash

echo "=========================="
echo "Installing App vsl"

# Here is where we perform installation of scripts, services, etc.
echo " - Installing ROS packages for VSL..."

LIBPANDA_SRC=$(cat /etc/libpanda.d/libpanda_src_dir)
LIBPANDA_USER=$(cat /etc/libpanda.d/libpanda_usr)

source /home/$LIBPANDA_USER/.bashrc

runuser -l $LIBPANDA_USER -c /etc/libpanda.d/apps/cbf/installRosPackagesForVsl.sh

echo "Installing VSL demo..."
runuser -l $LIBPANDA_USER -c /etc/libpanda.d/apps/cbf/installVslController.sh
