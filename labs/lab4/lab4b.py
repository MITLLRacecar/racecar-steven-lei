"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 4B - LIDAR Wall Following
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
    print(">> Lab 4B - LIDAR Wall Following")



def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    
    # right_dist = rc_utils.get_lidar_closest_point(scan, (80,100))[1]
    # left_dist = rc_utils.get_lidar_closest_point(scan, (260,280))[1]
    angle = 0
    speed = 0
    # TODO: Follow the wall to the right of the car without hitting anything.

    scan = rc.lidar.get_samples()
    sectors = 10
    window_length = 180
    window_start = -90
    windows = [[window_start +  w *window_length//sectors, window_start + (w+1) *window_length//sectors-1] for w in range(sectors)]
    
    sector_index = 0
    sector_distance = 0
    
    for i in range(len(windows)):
        temp = rc_utils.get_lidar_closest_point(scan, windows[i])[1]
        if temp > sector_distance:
            sector_index = i
            sector_distance = temp
    

    angle = (windows[sector_index][0] + windows[sector_index][1]) / 2
    angle = rc_utils.remap_range(angle, window_start, window_start+window_length, -1, 1, True) *2
    angle = rc_utils.clamp(angle,-1,1)
    
    speed = 0.85
    
    rc.drive.set_speed_angle(speed, angle)

    if rc.controller.is_down(rc.controller.Button.B):
        # print("Front:", front_dist, "Back:", back_dist, "Left:", left_dist, "Right", right_dist)
        print("Angle:", angle,)
    if rc.controller.is_down(rc.controller.Button.A):
        print("Windows:", windows)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
