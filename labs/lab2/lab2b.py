"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 2B - Color Image Cone Parking
"""

########################################################################################
# Imports
########################################################################################

import sys
from typing import Counter
import cv2 as cv
import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

from enum import IntEnum

class State(IntEnum):
    search = 0
    obstacle = 1
    approach = 2
    stop = 3

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

curr_state: State = State.search

counter = 0
# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# The HSV range for the color orange, stored as (hsv_min, hsv_max)
ORANGE = ((10, 100, 100), (20, 255, 255))

MIN_AREA_THRESHOLD = 27500
MAX_AREA_THRESHOLD = 28000
# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

########################################################################################
# Functions
########################################################################################


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


def start():
    """
    This function is run once every time the start button is pressed
    """
    global speed
    global angle

    global curr_state
    curr_state = State.search

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # Print start message
    print(">> Lab 2B - Color Image Cone Parking")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global speed
    global angle
    global counter
    global curr_state
    # Search for contours in the current color image
    update_contour()

    # TODO: Park the car 30 cm away from the closest orange cone
    
    # move randomly
    if curr_state == State.search:
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
        
        elif contour_center[0] > 388:
            curr_state = State.stop
    #30 cm : 388 px ht
        else:
            angle = remap(contour_center[1], 0, rc.camera.get_width(), -1, 1)
            speed = speed_remap(contour_center[0], 0, 388, 1, 0)
            # speed = 0.5
        
    if curr_state == State.stop:
        speed = 0

    rc.drive.set_speed_angle(speed, angle)
    
    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("State:", curr_state, "Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)
            

def remap(val,old_min,old_max,new_min,new_max):

    len1 = abs(old_max - old_min)
    len2 = abs(new_max - new_min)
    scale = val/len1
    scale_shift = scale*len2
    if new_max > new_min:
        val = new_min + scale_shift
    else:
        val = new_min - scale_shift

    if val > new_max:
        val = new_max
    elif val < new_min:
        val = new_min
    return val

def speed_remap(val,old_min,old_max,new_min,new_max):
    dist_old = abs(old_min-old_max)
    dist_new = abs(new_max-new_min)
    
    scale = dist_new/dist_old
    
    val = abs(val - old_min) * scale

    if (new_min > new_max):
        val = new_min - val
    else:
        val = new_min + val
        
    # if val >= new_max:
    #     val = new_max
    # elif val <= new_min:
    #     val = new_min
    return val

def update_slow():
    """
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """
    # Print a line of ascii text denoting the contour area and x position
    if rc.camera.get_color_image() is None:
        # If no image is found, print all X's and don't display an image
        print("X" * 10 + " (No image) " + "X" * 10)
    else:
        # If an image is found but no contour is found, print all dashes
        if contour_center is None:
            print("-" * 32 + " : area = " + str(contour_area))

        # Otherwise, print a line of dashes with a | indicating the contour x-position
        else:
            s = ["-"] * 32
            s[int(contour_center[1] / 20)] = "|"
            print("".join(s) + " : area = " + str(contour_area))


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
