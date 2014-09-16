import nengo_pushbot

import nengo

model = nengo.Network()
with model:
# change this like to correspond to your robot ip
    bot = nengo_pushbot.PushBotNetwork('10.162.177.43')
    bot.track_freqs([200])
    bot.laser(200)
    #bot.show_image()

    pos1 = nengo.Ensemble(100, 3, label='pos1')
    nengo.Connection(bot.tracker_0, pos1)

    def orient(x):
        if x[0] > 0.6 and x[2] > 0.6:
			print x[0], x[2]
			return [1, 1]
        else:
            return [0, 0]

    nengo.Connection(pos1, bot.motor, function=orient, 
                     transform=0.2, synapse=0.003)
    nengo.Probe(pos1)
    
if __name__ == '__main__':

    '''start the nengo gui for circuit visulisation'''
    #import nengo_gui.javaviz
    #jv = nengo_gui.javaviz.View(model)
    sim = nengo.Simulator(model)
    #jv.update_model(sim)
    #jv.view()
    sim.run(1000)
  
