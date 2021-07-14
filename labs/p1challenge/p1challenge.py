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
MIN_CONTOUR_AREA = 300
contour_red_center = 0.0
contour_red_area = 0
contour_blue_center = 0.0
contour_blue_area = 0
color = True

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
        contour_center = None
        contour_area = 0
    else:
        # Find all blue and red contours
        contours_red = rc_utils.find_contours(image, RED[0], RED[1])

        # Select the largest contour of each color
        contour_red = rc_utils.get_largest_contour(contours_red, MIN_CONTOUR_AREA)
        
        #Find the contour area of each color
        red_area = rc_utils.get_contour_area(contour_red) if contour_red is not None else 0.0

        contour = contour_red

        if contour is not None:
            # Calculate contour information
            contour_red_center = rc_utils.get_contour_center(contour)
            contour_red_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_red_center)            
            # rc_utils.draw_circle(image, [contour_center[0], contour_center[1] + OFFSET_DIST])
        else:
            contour_red_center = None
            contour_red_area = 0

        return contour
        # Display the image to the screen
        #rc.display.show_color_image(image)

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
        contour_center = None
        contour_area = 0
    else:
        # Find all blue and red contours
        contours_blue = rc_utils.find_contours(image, BLUE[0], BLUE[1])

        # Select the largest contour of each color
        contour_blue = rc_utils.get_largest_contour(contours_blue, MIN_CONTOUR_AREA)
        
        #Find the contour area of each color
        blue_area = rc_utils.get_contour_area(contour_blue) if contour_blue is not None else 0.0

        contour = contour_blue

        if contour is not None:
            # Calculate contour information
            contour_blue_center = rc_utils.get_contour_center(contour)
            contour_blue_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_blue_center)            
            # rc_utils.draw_circle(image, [contour_center[0], contour_center[1] + OFFSET_DIST])

        else:
            contour_blue_center = None
            contour_blue_area = 0

        return contour
        # Display the image to the screen
        #rc.display.show_color_image(image)

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
    global color
    global OFFSET_DIST
    global curr_state
    
    red_contour = update_red_contour()
    blue_contour = update_blue_contour()
    
    image = rc.camera.get_color_image()

    if curr_state == State.search:
        if red_contour and blue_contour:
            curr_state = State.approach_red if contour_red_area > contour_blue_area else State.approach_blue
        elif red_contour:
            curr_state = State.approach_red
        elif blue_contour:
            curr_state = State.approach_blue
        angle = 0.5
        speed = 0.5
    elif curr_state == State.approach_red:
        mask = get_mask(image, RED[0], RED[1])
        closest_point = contour_red_center
    elif curr_state == State.approach_blue:
        mask = get_mask(image, BLUE[0], BLUE[1]) 
        closest_point = contour_blue_center

    
    
    # mask = get_mask(image, RED[0], RED[1]) if color else get_mask(image, BLUE[0], BLUE[1])
    # masked_image = cv.bitwise_and(image, image, mask=mask)
    
    depth_image = rc.camera.get_depth_image() * mask
    closest_distance = depth_image[closest_point[0]][closest_point[1]]  / 255
    
    rc_utils.draw_circle(depth_image, closest_point)            
    
    # rc.display.show_color_image(rc_utils.colormap_depth_image(depth_image / 255, 1000))

    if closest_distance < 30:
        OFFSET_DIST = 150
    else:
        OFFSET_DIST = 75
    
    if curr_state == State.approach_red:
        angle = rc_utils.remap_range(contour_red_center[1] + OFFSET_DIST, 0, 640, -0.25, 1, True)

    elif curr_state == State.approach_blue:
        angle = rc_utils.remap_range(contour_blue_center[1] + OFFSET_DIST, 0, 640, -1, 0.25, True)
    
    speed = 0.25
    
    
    
    rc.drive.set_speed_angle(speed, angle)

    #Debug
    if rc.controller.is_down(rc.controller.Button.A):
        print(f"State:{color} Speed{speed:.2f} Angle: {angle} Area:{}")
    if rc.controller.is_down(rc.controller.Button.B):
        # print(f"Closest point distance:{depth_image[closest_point[0]][closest_point[1]]} ")
        print(f" ")



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
