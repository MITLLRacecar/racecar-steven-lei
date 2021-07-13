"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3A - Depth Camera Safety Stop
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
import statistics as stat

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here
safety_stop = False
########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(
        ">> Lab 3A - Depth Camera Safety Stop\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Right bumper = override safety stop\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = print current speed and angle\n"
        "    B button = print the distance at the center of the depth image"
    )


def update():
    
    global safety_stop

    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)
    
    # center_line = depth_image[rc.camera.get_height()//3:rc.camera.get_height()*2 //3, rc.camera.get_width()//2]
    # std = np.std(center_line)

    # TODO (stretch goal): Tune safety stop so that the car is still able to drive up
    # and down gentle ramps.
    # Hint: You may need to check distance at multiple points.
    ramp = False
    top_depth = depth_image[rc.camera.get_height()//2, rc.camera.get_width() //2]
    middle_depth = depth_image[rc.camera.get_height()//2 + 30, rc.camera.get_width() //2]
    bottom_depth = depth_image[rc.camera.get_height()//2 + 60, rc.camera.get_width() //2]

    if 5 < middle_depth - bottom_depth < 100  or 5 < top_depth - middle_depth < 100:
        ramp  = True
    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.

    if 0 < center_distance < 100:
        if ramp:
            safety_stop = False
        else:
            safety_stop = True
    else:
        safety_stop = False
    # if 10 < std < 40:
    #     safety_stop = False
   
    # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
    # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.

    line_depth = depth_image[rc.camera.get_height()//2 + 200][rc.camera.get_width()//2]
    if line_depth > 100:
        safety_stop = True

    
    
    if rc.controller.is_down(rc.controller.Button.RB):
        safety_stop = False
    
    if safety_stop and center_distance > 50:
        speed = -0.5
    elif safety_stop and center_distance <=50:
        speed = 0
    elif safety_stop:
        speed = 0

 
    # Use the left joystick to control the angle of the front wheels
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)
    rc.display.show_depth_image(depth_image)


    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    if rc.controller.is_down(rc.controller.Button.B):
        print("Center distance:", center_distance, "Line depth:", line_depth, "Depths", top_depth, middle_depth, bottom_depth )

    # Display the current depth image
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
