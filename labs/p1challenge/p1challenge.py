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

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils
from enum import IntEnum

class State(IntEnum):
    search  = 0
    approach_red = 1
    approach_blue = 2
    stop = 3

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

curr_state: State = State.search

speed = 0.0
angle = 0.0

#HSV Values
BLUE = ((100, 175, 200), (130, 255, 255))  # The HSV range for the color blue
RED  = ((170, 50, 50),(179, 255, 255))

##Contour stuff
MIN_CONTOUR_AREA = 200
contour_red_center = 0.0
contour_red_area = 0
contour_blue_center = 0.0
contour_blue_area = 0

# Distance to look beside center of cone
OFFSET_DIST = 75

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()
    curr_state = State.search
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
    global contour_red_center
    global contour_blue_center
    global contour_red_area
    global contour_blue_area
    global OFFSET_DIST
    global curr_state

    red_contour = update_red_contour()
    blue_contour = update_blue_contour()
    
    image = rc.camera.get_color_image()
    depth_image_original = rc.camera.get_depth_image()
    
    # closest_point = None
    # mask = None
    # if curr_state == State.search:
    #     if red_contour is not None and blue_contour is not None :
    #         curr_state = State.approach_red if contour_red_area > contour_blue_area else State.approach_blue
    #     elif red_contour is not None:
    #         curr_state = State.approach_red
    #     elif blue_contour is not None:
    #         curr_state = State.approach_blue
    #     angle = 0.5
    #     speed = 0.5
    # elif curr_state == State.approach_red:
    #     if red_contour is None:
    #         curr_state = State.search
    #     mask = get_mask(image, RED[0], RED[1])
    #     closest_point = contour_red_center

    # elif curr_state == State.approach_blue:
    #     if blue_contour is None:
    #         curr_state = State.search
    #     mask = get_mask(image, BLUE[0], BLUE[1]) 
    #     closest_point = contour_blue_center
    red_depth = 0.0
    blue_depth = 0.0
    if curr_state == State.search:
        if red_contour is not None and blue_contour is not None:
            red_depth = depth_image_original[contour_red_center[0]][contour_red_center[1]]
            blue_depth = depth_image_original[contour_blue_center[0]][contour_blue_center[1]]
            if red_depth < blue_depth:
                curr_state = State.approach_red
            elif blue_depth < red_depth:
                curr_state = State.approach_blue
            
        elif red_contour is not None:
            curr_state = State.approach_red
        elif blue_contour is not None:
            curr_state = State.approach_blue
        else:
            speed = 0.5
            angle = 0.5
    
    OFFSET_DIST = 90
    if curr_state == State.approach_red:
        if red_contour is None:
            curr_state = State.search
        else:
            red_depth = depth_image_original[contour_red_center[0]][contour_red_center[1]]
            angle = rc_utils.remap_range(contour_red_center[1] + OFFSET_DIST, 0, 640, -0.35, 1, True)
            rc_utils.draw_circle(image, [contour_red_center[0] , contour_red_center[1] + OFFSET_DIST])            
 
    if curr_state == State.approach_blue:
        if blue_contour is None:
            curr_state = State.search
        else:
            blue_depth = depth_image_original[contour_blue_center[0]][contour_blue_center[1]]
            angle = rc_utils.remap_range(contour_blue_center[1] - OFFSET_DIST, 0, 640, -1, 0.35, True)
            rc_utils.draw_circle(image, [contour_blue_center[0] , contour_blue_center[1] - OFFSET_DIST])   
   
    speed = 0.5  
    
    rc.drive.set_speed_angle(speed, angle)
    rc.display.show_color_image(image)    

    #Debug
    if rc.controller.is_down(rc.controller.Button.A):
        print(f"State:{curr_state} Speed{speed:.2f} Angle: {angle}")
    if rc.controller.is_down(rc.controller.Button.B):
        print(f"Red depth:{red_depth} Blue depth:{blue_depth} Red area: {contour_red_area} Blue area: {contour_blue_area}")


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
