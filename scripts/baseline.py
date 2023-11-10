#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64, Int16, String, Bool
import traceback

velocity_topic = "/car/state/vel_x"
set_speed_topic = "/cmd_vel"

velocity = 0

def velocity_callback(data):
    global velocity
    velocity = data.data

class baseline:
    def __init__(self):
        rospy.init_node('baseline', anonymous=True)

        rospy.Subscriber(velocity_topic,Float64,velocity_callback)

        global current_set_speed_pub
        current_set_speed_pub = rospy.Publisher(set_speed_topic, Float64, queue_size=1000)

        self.rate = rospy.Rate(20)

    def loop(self):
        while not rospy.is_shutdown():
            try:
                global velocity
                current_set_speed_pub.publish(velocity)

            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Something has gone wrong.")
            self.rate.sleep()

if __name__ == '__main__':
    try:
        head = baseline()
        head.loop()
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("An exception occurred")
