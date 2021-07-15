"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Phase 1 Challenge - Cone Slaloming
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
import math as mt
sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils
from enum import IntEnum

class State(IntEnum):
    search  = 0
    approach_red = 1
    approach_blue = 2
    turn_red = 3
    turn_blue = 4
    stop = 5

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

curr_state: State = State.search

speed = 0.0
angle = 0.0

#HSV Values
BLUE = ((100, 175, 200), (130, 255, 255))  # The HSV range for the color blue
RED  = ((165, 0, 0),(179, 255, 255)) 
##Contour stuff
MIN_CONTOUR_AREA = 300
contour_red_center = 0.0
contour_red_area = 0
contour_blue_center = 0.0
contour_blue_area = 0
# Distance to look beside center of cone
OFFSET_DIST = 75
# Cone recovery
RECOVER_BLUE = False
RECOVER_RED = False

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
    print(">> Phase 1 Challenge: Cone Slaloming")

def update_red_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_red_center
    global contour_red_area
    global RED

    image = rc.camera.get_color_image()

    if image is None:
        contour_red_center = None
        contour_red_area = 0
    else:
        # Find all blue and red contours
        contours_red = rc_utils.find_contours(image, RED[0], RED[1])

        # Select the largest contour of each color
        contour_red = rc_utils.get_largest_contour(contours_red, MIN_CONTOUR_AREA)
    
        contour = contour_red
        
        if contour is not None:
            # Calculate contour information
            contour_red_center = rc_utils.get_contour_center(contour)
            contour_red_area = rc_utils.get_contour_area(contour)        
        else:
            contour_red_center = None
            contour_red_area = 0
        return contour
        

def update_blue_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_blue_center
    global contour_blue_area
    global BLUE

    image = rc.camera.get_color_image()

    if image is None:
        contour_blue_center = None
        contour_blue_area = 0
    else:
        # Find all blue and red contours
        contours_blue = rc_utils.find_contours(image, BLUE[0], BLUE[1])

        # Select the largest contour of each color
        contour_blue = rc_utils.get_largest_contour(contours_blue, MIN_CONTOUR_AREA)
        
        #Find the contour area of each color

        contour = contour_blue

        if contour is not None:
            # Calculate contour information
            contour_blue_center = rc_utils.get_contour_center(contour)
            contour_blue_area = rc_utils.get_contour_area(contour)

        else:
            contour_blue_center = None
            contour_blue_area = 0

        return contour


def get_mask(image, hsv_lower, hsv_upper):
    """   
    Returns a mask containing all of the areas of image which were between hsv_lower and hsv_upper.
    
    Args:
        image: The image (stored in BGR) from which to create a mask.
        hsv_lower: The lower bound of HSV values to include in the mask.
        hsv_upper: The upper bound of HSV values to include in the mask.
    """
    # Convert hsv_lower and hsv_upper to numpy arrays so they can be used by OpenCV
    hsv_lower = np.array(hsv_lower)
    hsv_upper = np.array(hsv_upper)
    
    # TODO: Use the cv.cvtColor function to switch our BGR colors to HSV colors
    img_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # TODO: Use the cv.inRange function to highlight areas in the correct range
    mask = cv.inRange(img_hsv, hsv_lower, hsv_upper)
    
    return mask

def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Slalom between red and blue cones.  The car should pass to the right of
    # each red cone and the left of each blue cone.
    global angle
    global speed
    global contour_red_center, contour_blue_center
    global contour_red_area, contour_blue_area
    global OFFSET_DIST
    global curr_state
    global RECOVER_BLUE, RECOVER_RED
    
    red_contour = update_red_contour()
    blue_contour = update_blue_contour()
    
    image = rc.camera.get_color_image()
    depth_image_original = rc.camera.get_depth_image()
    
  
    red_depth = depth_image_original[contour_red_center[0]][contour_red_center[1]] if red_contour is not None else 0.0
    blue_depth = depth_image_original[contour_blue_center[0]][contour_blue_center[1]] if blue_contour is not None else 0.0
    
    # we want to identify the closest object

    if curr_state == State.search:
        # only approach the red cone iff it exists and it is closer
        if (red_depth < blue_depth or blue_depth == 0) and red_depth!=0 :
            curr_state = State.approach_red
        #approach the blue cone iff it exists and its closer
        elif (blue_depth < red_depth or red_depth == 0) and blue_depth !=0:
            curr_state = State.approach_blue
        
        # else we drive and search
        elif RECOVER_RED:
            angle = -1
            speed = 1
        elif RECOVER_BLUE:
            angle = 1
            speed = 1
        else:
            speed = 0.5
            
    
    OFFSET_DIST = 30
    v_const = 60

    if curr_state == State.approach_red:
        # swap to blue iff it exists and is closer
        if blue_depth < red_depth and blue_depth!=0:
            curr_state = State.approach_blue

        #go back to search if its gone
        elif red_depth == 0:
            curr_state = State.search
        else:
            # OFFSET_DIST = int(mt.sqrt(abs(v_const**2 + red_depth**2 - 2*v_const * red_depth  * v_const / red_depth)))
            # angle = rc_utils.remap_range(contour_red_center[1] + OFFSET_DIST, 0, 640, -0.35, 1, True) 
            angle = rc_utils.remap_range(red_depth, 150, 0, 0, 1, True)

            rc_utils.draw_contour(image, red_contour)
            rc_utils.draw_circle(image, [contour_red_center[0] , contour_red_center[1]])    
            RECOVER_RED = True        
 
    if curr_state == State.approach_blue:
        if RECOVER_RED: RECOVER_RED = False
        if red_depth < blue_depth and red_depth!=0:
            curr_state = State.approach_red
        
        elif blue_depth == 0:
            curr_state = State.search
        else:
            # OFFSET_DIST = int(mt.sqrt(abs(v_const**2 + red_depth**2 - 2*v_const * red_depth  * v_const / red_depth)))
            # angle = rc_utils.remap_range(contour_blue_center[1] - OFFSET_DIST, 0, 640, -1, 0.35, True)
            angle = rc_utils.remap_range(blue_depth, 150, 0, 0, -1, True)
            rc_utils.draw_contour(image, blue_contour)
            rc_utils.draw_circle(image, [contour_blue_center[0] , contour_blue_center[1]])
            RECOVER_BLUE = True   
   
    speed = 0.5
    
    rc.drive.set_speed_angle(speed, angle)
    rc.display.show_color_image(image)

    #######################################
    ###############Debug###################
    #######################################

    if rc.controller.is_down(rc.controller.Button.A):
        print(f"State:{curr_state} Speed{speed:.2f} Angle: {angle:.2f}")
        print(f"Red depth:{red_depth:.2F} Blue depth:{blue_depth:.2F} Red area: {contour_red_area:.2f} Blue area: {contour_blue_area:.2f}")

    if rc.controller.is_down(rc.controller.Button.B):
        print(f"Red depth:{red_depth:.2F} Blue depth:{blue_depth:.2F} Red area: {contour_red_area:.2f} Blue area: {contour_blue_area:.2f}")

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
