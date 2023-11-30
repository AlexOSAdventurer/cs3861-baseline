#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64, Int16, String
from sensor_msgs.msg import NavSatFix, TimeReference
import traceback
import os
import sys
import requests
import time
import bisect
import numpy as np

velocity_topic = "/car/state/vel_x"
acceleration_topic = "/car/state/imu_x"
acc_speed_topic = "acc/set_speed2"
acc_status_topic = "acc/cruise_state_int"

velocity = 0.0
acceleration = 0.0
acc_speed = 20
acc_status = None
can_update_time = None

gps_fix_topic = "gps_fix"
gps_fix_time_reference_topic = "gps_fix_time"
gpstime = None
systime = None
latitude = None
longitude = None
status = None
gps_update_time = None

vin=None
vin_path="/etc/libpanda.d/vin"
web_path="http://ransom.isis.vanderbilt.edu/junyi_musketeer_project/rest.php"

def readAllFile(path):
    assert os.path.exists(path), path + " file does not exist apparently!"
    file = open(path, mode='r')
    res = file.read()
    file.close()
    return res

def getVIN():
    return readAllFile(vin_path)

def velocity_callback(data):
    global velocity
    global can_update_time
    velocity = data.data
    can_update_time = rospy.Time.now()

'''def acceleration_callback(data):
    global acceleration
    global can_update_time
    acceleration = data.data
    can_update_time = rospy.Time.now()
'''

def acc_speed_callback(data):
    global acc_speed
    global can_update_time
    acc_speed = data.data
    if acc_speed >= 127:
        acc_speed=127
    can_update_time = rospy.Time.now()

def acc_status_callback(data):
    global acc_status
    global can_update_time
    acc_status = data.data
    can_update_time = rospy.Time.now()

def gps_fix_callback(data):
    global systime
    global latitude
    global longitude
    global status
    global gps_update_time

    latitude = data.latitude
    longitude = data.longitude
    status = data.status.status
    systime = rospy.Time.now()
    gps_update_time = systime

def gps_fix_time_reference_callback(data):
    global gpstime
    gpstime = data.time_ref

def getGPSResultStr():
    global gpstime
    global systime
    global latitude
    global longitude
    global status
    return ",".join(['{}'.format(int(gpstime.to_sec() * 1000)), '{}'.format(int(systime.to_sec() * 1000)), str(latitude), str(longitude), str(status)])

def getCANResultStr():
    global velocity
    global acceleration
    global acc_status
    global acc_speed
    acc_status_int = {25: 1}.get(acc_status, 0)
    return ",".join([str(velocity), str(acceleration), str(acc_status_int), str(acc_speed)])

class LiveTracker:
    def __init__(self):
        global vin
        rospy.init_node('LiveTracker', anonymous=True)
        rospy.Subscriber(velocity_topic, Float64, velocity_callback)
        #rospy.Subscriber(acceleration_topic, Float64, acceleration_callback)
        rospy.Subscriber(acc_speed_topic, Float64, acc_speed_callback)
        rospy.Subscriber(acc_status_topic, Int16, acc_status_callback)
        rospy.Subscriber(gps_fix_topic, NavSatFix, gps_fix_callback)
        rospy.Subscriber(gps_fix_time_reference_topic, TimeReference, gps_fix_time_reference_callback)

        self.rate = rospy.Rate(1)
        while vin is None:
            try:
                vin = getVIN()
            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Cannot get VIN at this time!")
                time.sleep(1.0)  # Wait 1 second hard-coded between checking for the VIN file

    def loop(self):
        while not rospy.is_shutdown():
            try:
                global vin
                current_time = rospy.Time.now()
                assert gps_update_time is not None, "GPS data has never been received!"
                assert can_update_time is not None, "CAN data has never been received!"
                assert abs((current_time - gps_update_time).to_sec()) < 30, "GPS data more than 30 seconds old!"
                assert abs((current_time - can_update_time).to_sec()) < 30, "CAN data more than 30 seconds old!"

                gps = getGPSResultStr()
                can = getCANResultStr()
                data_str = ",".join(["?circles", vin, gps, can])
                get_str = web_path + data_str
                print(get_str)
                print(requests.get(get_str))

            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Not uploading any data at this time.")
            self.rate.sleep()

if __name__ == '__main__':
    try:
        tracker = LiveTracker()
        tracker.loop()
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("An exception occurred")
