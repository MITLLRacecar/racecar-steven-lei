"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3B - Depth Camera Cone Parking
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
from enum import IntEnum

class State (IntEnum):
    search = 0
    approach = 1
    stop = 2
    reverse = 3

########################################################################################
# Global variables
########################################################################################
curr_state: State = State.search
rc = racecar_core.create_racecar()

counter = 0
# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 25

# The HSV range for the color orange, stored as (hsv_min, hsv_max)
ORANGE = ((10, 100, 100), (20, 255, 255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

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
    print(">> Lab 3B - Depth Camera Cone Parking")

def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Find all of the orange contours
        contours = rc_utils.find_contours(image, ORANGE[0], ORANGE[1])

        # Select the largest contour
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            # Calculate contour information
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)

        else:
            contour_center = None
            contour_area = 0

        # Display the image to the screen
        rc.display.show_color_image(image)

def update():
    global speed
    global angle
    global counter
    global curr_state

    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 30 cm away from the closest orange cone.
    # Use both color and depth information to handle cones of multiple sizes.
    # You may wish to copy some of your code from lab2b.py
    update_contour()
    depth_image = rc.camera.get_depth_image()
    center_cone_distance = 0.0
    if contour_center is not None:
        center_cone_distance = depth_image[contour_center[0]][contour_center[1]]

    if curr_state == State.search:
        #drives in a figure8
        angle = 1
        speed = 0.5
        if counter % 10 < 8:
            angle = -1

        counter += rc.get_delta_time()
        
        if contour_area > MIN_CONTOUR_AREA:
            curr_state = State.approach

    if curr_state == State.approach: 

        if contour_area < MIN_CONTOUR_AREA:
            curr_state = State.search
        
        elif center_cone_distance < 30.5:
            curr_state = State.stop
    
    #30 cm : 388 px ht
        else:
            angle = remap_range(contour_center[1], 0, rc.camera.get_width(), -1, 1)
            speed = remap_range(center_cone_distance, 0, 200, 0, 0.5)
    
    
    if curr_state == State.stop:
        if  center_cone_distance < 29.5:
            curr_state = State.reverse
        if center_cone_distance == 0.0:
            curr_state = State.search
        else:
            speed = 0   
    
    if curr_state == State.reverse:
        speed = -0.1
        if center_cone_distance > 29.5:
            curr_state = State.stop

    rc.drive.set_speed_angle(speed, angle)
    
    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("State:", curr_state, "Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area, "Center Distance:", center_cone_distance)
    

def remap_range(val: float, old_min: float, old_max: float, new_min: float, new_max: float,) -> float:
        
    old_range = old_max - old_min
    new_range = new_max - new_min
    shift = new_range / old_range
    val = ((val- old_min) * shift) + new_min
    return clamp(val,new_min,new_max)

def clamp(val, min, max):
    if val > max: return max
    if val < min: return min
    return val


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
