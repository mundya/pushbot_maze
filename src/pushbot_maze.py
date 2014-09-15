import time
import numpy as np
from nengo_pushbot import PushBot3
import nengo_pushbot
import nengo

if __name__ == '__main__':

    IP = raw_input("Please enter the robot IP: ")
    print "IP address entered is: ", IP
    bot = PushBot3(IP, packet_size=4)
    #bot = PushBot3('1,0,EAST')
    #bot.activate_sensor('compass', freq=100)
    #bot.activate_sensor('gyro', freq=100)
    #bot.count_spikes(all=(0,0,128,128), left=(0,0,64,128), right=(64,0,128,128))
    #bot.activate_sensor('bat', freq=100)
    #bot.track_freqs([300, 200, 100], sigma_p=40)
    bot.show_image()
    #import time
    
    '''turn on laser for object avoidance'''
    bot.laser(200)
    '''read where the laser pointer is and print to screen'''
    laser_pos = bot.track_freqs([200], sigma_p=40)
    '''stop when we see the laser is a certain distance (threshold down the screen) - this will be updated to turn left or right'''
   
    '''see another laser at certain distance'''
    
    '''record sensory data at point of inflection'''
    

    while True:
        # find the x and y position of the laser point in the field of view
        # TODO: need to return labelled positions for each different frequency 
        x = bot.p_x
        y = bot.p_y
        print x,y
        # if the bot is to close to the wall turn left 
        # TODO: need to make this a random routine that will update with learning 
        if y < 47:
            bot.motor(0, 0.3, 0)
        else:
            bot.motor(0.2, 0.2, 0)

            
        time.sleep(0.1)

