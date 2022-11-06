#!/usr/bin/env python3

import rospy
import traceback
import time
import sensor_msgs.msg
from ackermann_msgs.msg import AckermannDriveStamped
from jetracer.nvidia_racecar import NvidiaRacecar

class JetRacerTeleopException(Exception):
    pass


class JetRacerTeleop:
    """
    Jetracer joystick teleoperation node.
    Will not start without configuration, has to be stored in 'jetracer' parameter.
    jetracer.yaml for an example.
    """
    def __init__(self):
        rospy.init_node('jetracer_teleop')

        if not rospy.has_param('jetracer'):
            raise JetRacerTeleopException('JetRacerTeleop jetracer paramater is not configured')


        self.previostime = -1
        self.previosvel = 0
        self.previosaccel = 0


        jet_racer = rospy.get_param("jetracer")
        cntrlr =  jet_racer.get('controller', {})
        self.cntrlr = cntrlr
        self.steering =  cntrlr.get('steering', 0)
        self.throttle =  cntrlr.get('throttle', 0)
        self.velocity_gain =  jet_racer.get('velocity_gain', 1)
        self.steering_gain =  jet_racer.get('steering_gain', 0.41)
        self.frame_id =  jet_racer.get('frame_id', 'odom')
        rospy.loginfo("JetRacerTeleop starting")
        
        self.car = NvidiaRacecar()
        

        throttle_gain =  jet_racer.get('throttle_gain', 0.3)
        steering_offset =  jet_racer.get('steering_offset', 0)
        self.car.throttle_gain = throttle_gain
        self.car.steering_offset= steering_offset
        self.car.steering = 0
        
        joytopic =   jet_racer.get('joytopic', 'joy')
        self.joysub = rospy.Subscriber(joytopic, sensor_msgs.msg.Joy, self.joy_callback)
        drivetopic =   jet_racer.get('drivetopic', 'drive')
        self.ackermanpub = rospy.Publisher(drivetopic, AckermannDriveStamped, queue_size=1)



    def joy_callback(self, data):
        try:
           steering = data.axes[self.steering]
           throttle = data.axes[self.throttle]
           rospy.loginfo("JetRacerTeleop steering {} throttle {}".format(steering, throttle))
           self.car.steering = steering
           self.car.throttle = throttle
           self.publish_drive()
        except JetRacerTeleopException as e:
            rospy.logerr("error while parsing joystick input: %s", str(e))
        self.old_buttons = data.buttons

    def publish_drive(self):
        v =  self.car.throttle * self.velocity_gain
        accel = 0.0
        jerk = 0.0
        if self.previostime > 0:
            currenttime = time.time()
            delta_t = currenttime - self.previostime
            delta_v = v - self.previosvel
            accel = delta_v/delta_t
            delta_a = accel - self.previosaccel
            jerk = delta_a / delta_t
            self.previostime = currenttime
            self.previosvel = v
            self.previosaccel = accel
        else:
            self.previostime = time.time()
            self.previosvel = v
            self.previosaccel = 0
        msg = AckermannDriveStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.frame_id
        msg.drive.steering_angle = self.car.steering * self.steering_gain
        msg.drive.speed = v
        msg.drive.acceleration = accel
        msg.drive.jerk = jerk
        self.ackermanpub.publish(msg)

if __name__ == "__main__":
    try:
        jt = JetRacerTeleop()
        rospy.spin()
    except JetRacerTeleopException:
        rospy.logfatal("no configuration was found, taking node down")
        pass
    except rospy.ROSInterruptException:
        pass
    except Exception as ex:
        traceback.print_exception(type(ex), ex, ex.__traceback__)

       
