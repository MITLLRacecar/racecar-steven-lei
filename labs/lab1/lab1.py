"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 1 - Driving in Shapes
"""

########################################################################################
# Imports
########################################################################################

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()
velo = 0
angle = 0
counter = 0
mode = "User"
# Put any global variables here

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    rc.drive.stop()

    # Print start message
    # TODO (main challenge): add a line explaining what the Y button does
    print(
        ">> Lab 1 - Driving in Shapes\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = drive in a circle\n"
        "    B button = drive in a square\n"
        "    X button = drive in a figure eight\n"
        "    Y button = drive in a triangle\n"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global counter
    global velo
    global angle
    global circling
    global mode

    TriggerLeft = rc.controller.Trigger.LEFT
    TriggerRight = rc.controller.Trigger.RIGHT
    
    velo = rc.controller.get_trigger(TriggerLeft)-rc.controller.get_trigger(TriggerRight)
    
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    # print(f"{velo} and {angle}")

    rc.drive.set_speed_angle(velo, angle)    

    if rc.controller.was_pressed(rc.controller.Button.A):
        mode = "Circle"
        print("Driving in a circle...")
    if rc.controller.was_pressed(rc.controller.Button.B):
        mode = "Square"
        counter = 0
        print("Driving in a square")
    if rc.controller.was_pressed(rc.controller.Button.X):
        mode = "Figure8"
        counter = 0
        print("Driving in a figure 8")
    if rc.controller.was_pressed(rc.controller.Button.Y):
        mode = "DrawS"
        counter = 0
        print("Driving in a S")

    # Drives in a circle
    if(mode == "Circle"):
        rc.drive.set_speed_angle(1,0.5)
    
    # Drives in a square
    if(mode == "Square"):
        # in seconds
        per = 6
        angle = 0
        turn_angle = 1
        velo = 0.75
        if(counter % per < 5.25):
            velo = 1
            angle = turn_angle
        if(counter % per <= 4):
            angle = 0
        rc.drive.set_speed_angle(velo,angle)
        counter+=rc.get_delta_time()
    
    #Drives in a figure 8 shape
    if(mode == "Figure8"):
        per = 10
        turn_angle = 1
        velo = 1
        if(counter % per < 5.5):
            turn_angle*=-1
        print(counter % 10)

        rc.drive.set_speed_angle(velo,turn_angle)
        counter+=rc.get_delta_time()

    if(mode == "DrawS"):
        per = 3.75
        turn_angle = 1
        velo = 1
        if(counter % per <= 2):
            turn_angle*=-1
        
        rc.drive.set_speed_angle(velo,turn_angle)
        counter+=rc.get_delta_time()

    # if rc.controller.was_pressed(rc.controller.Button.Y):
    #     mode = "User"



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
