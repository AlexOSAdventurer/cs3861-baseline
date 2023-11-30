#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64, Int16, String, Bool
import traceback
import requests
import time
import os
import json

pilot_velocity_topic = "/pilot_vel"
control_active_topic = "/control_active"
vin_path="/etc/libpanda.d/vin"
web_path="http://ransom.isis.vanderbilt.edu/junyi_musketeer_project/lead_car_velocity.php"

class LeadCarReceiver:
    def __init__(self):
        self.vin = None
        rospy.init_node('LeadCarReceiver', anonymous=True)

        self.pilot_velocity_pub = rospy.Publisher(pilot_velocity_topic, Float64, queue_size=1000)
        self.control_active_pub = rospy.Publisher(control_active_topic, Float64, queue_size=1000)

        self.rate = rospy.Rate(1)
        while self.vin is None:
            try:
                self.vin = self.getVIN()
            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Cannot get VIN at this time!")
                time.sleep(1.0)  # Wait 1 second hard-coded between checking for the VIN file

    def readAllFile(self, path):
        assert os.path.exists(path), path + " file does not exist apparently!"
        file = open(path, mode='r')
        res = file.read()
        file.close()
        return res

    def getVIN(self):
        return self.readAllFile(vin_path)

    def loop(self):
        while not rospy.is_shutdown():
            try:
                json_string = requests.get(web_path).content
                data = json.loads(json_string)
                if data["lead_car"] is not None:
                    lead_vin = data["lead_car"]["vin"]
                    lead_velocity = data["lead_car"]["velocity"]
                    lead_systime = data["lead_car"]["systime"]
                    self.pilot_velocity_pub.publish(lead_velocity)
                    self.control_active_pub.publish(self.vin != lead_vin)
                else:
                    self.pilot_velocity_pub.publish(0)
                    self.control_active_pub.publish(False)

            except Exception as e:
                print(e)
                traceback.print_exc()
            self.rate.sleep()

if __name__ == '__main__':
    try:
        receiver = LeadCarReceiver()
        receiver.loop()
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("An exception occurred")
