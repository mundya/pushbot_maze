import time
import numpy as np
from nengo_pushbot import PushBot3
import nengo_pushbot
import nengo

global IP 
IP = raw_input("Please enter the robot IP: ")
print "IP address entered is: ", IP

#~ model = nengo.Network()
#~ with model:
    #~ bot = nengo_pushbot.PushBotNetwork(IP)
#~ 
    #~ accel = nengo.Ensemble(300, 3, radius=2)
    #~ nengo.Connection(bot.accel, accel)
#~ 
    #~ direction = nengo.Ensemble(100, 2)
    #~ nengo.Connection(bot.compass[1:], direction)
#~ 
    #~ def orient(x):
        #~ target = [0, 1]
        #~ dot = -x[0]*target[1] + x[1]*target[0]
        #~ if dot > 0:
            #~ return [1, -1]
        #~ else:
            #~ return [-1, 1]
#~ 
    #~ nengo.Connection(direction, bot.motor, function=orient, transform=0.2)
#~ 
    #~ nengo.Probe(direction)
    #~ nengo.Probe(accel)
    #~ #nengo.Probe(direction, 'spikes')
#~ 


if __name__ == '__main__':

   
    bot = PushBot3(IP, packet_size=4)
    bot.show_image()
    
    '''turn on laser for object avoidance'''
    bot.laser(200)
    '''read where the laser pointer is and print to screen'''
    laser_pos = bot.track_freqs([200], sigma_p=40)
    '''see another laser at certain distance'''
    
    '''record sensory data at point of inflection SPA'''
    
    
    '''start the nengo gui for circuit visulisation'''
    #~ import nengo_gui.javaviz
    #~ jv = nengo_gui.javaviz.View(model)
    #~ sim = nengo.Simulator(model)
    #~ jv.update_model(sim)
    #~ jv.view()
    #~ 

    while True:
        #~ sim.run(1)
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

