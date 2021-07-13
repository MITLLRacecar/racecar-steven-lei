"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3C - Depth Camera Wall Parking
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()
counter = 0
# >> Constants

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels

turning = False #Has car turned towards wall yet

# Add any global variables here

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
    print(">> Lab 3C - Depth Camera Wall Parking")


def update():
    global speed
    global angle
    global turning
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 20 cm away from the closest wall with the car directly facing
    # the wall
    
    depth_image = rc.camera.get_depth_image()
    depth_image = depth_image[0:rc.camera.get_height()// 2][0:rc.camera.get_width()]
    rc.display.show_depth_image(depth_image)

    closest_pixel = rc_utils.get_closest_pixel(depth_image)
    closest_pixel_depth = depth_image[closest_pixel[0]][closest_pixel[1]]
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)

    if closest_pixel_depth < 150 and turning == False:
        speed = -0.5
        angle = -(rc_utils.remap_range(closest_pixel[1], 0, rc.camera.get_width(), -1,1))
    
    if closest_pixel_depth > 150:
        turning = True
        
    if turning == True:
        speed = 0.25
        angle = rc_utils.remap_range(closest_pixel[1], 0, rc.camera.get_width(), -1,1)

    if closest_pixel_depth < 22:
        speed = 0
        
    if closest_pixel_depth < 20:
        speed = -0.1
        
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle, "Depth", closest_pixel_depth, "Turning:", turning)
    
    rc.drive.set_speed_angle(speed, angle)
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
