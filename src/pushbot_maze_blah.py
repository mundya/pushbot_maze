import time
import numpy as np
from nengo_pushbot import PushBot3
import nengo_pushbot
import nengo

global IP 
IP = '10.162.177.43' #raw_input("Please enter the robot IP: ")
print "IP address entered is: ", IP

model = nengo.Network(label='pushbot')
with model:
    bot = nengo_pushbot.PushBotNetwork(IP)
    #bot.bot.show_image(decay=0.5)
    #laser set up
    bot.track_freqs([200])
    bot.laser(200)
    laser_pos = nengo.Ensemble(100, 3, label='laser_pos')
    nengo.Connection(bot.tracker_0, laser_pos)
    
    def avoid_obstacles(x):
    # if the bot is to close to the wall turn left 
    # TODO: need to make this a random routine that will update with learning 
		if x[0] > 0.6 and x[2] > 0.6:
			print x[0], x[2]
			return [-1, -1]
		else:
			return [1, 1]
            
        #~ if x[0] < 47:
            #~ return [0, 0.3, 0]
        #~ else:
            #~ return [0.2, 0.2, 0]
    
		nengo.Connection(laser_pos, bot.motor, function=avoid_obstacles, 
							transform=0.2, synapse=0.003)
		nengo.Probe(laser_pos)
	
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
    '''start the nengo gui for circuit visulisation'''
    #import nengo_gui.javaviz
    #jv = nengo_gui.javaviz.View(model)
    sim = nengo.Simulator(model)
    #jv.update_model(sim)
    #jv.view()
    sim.run(1000)
    
