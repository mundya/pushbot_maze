import nengo
import nengo.utils.functions
import nengo.utils.connection
import shelve
import os
import time

import nstbot

bot = nstbot.pushbot.PushBot()
bot.connect(nstbot.connection.Socket('10.162.177.135'))
bot.laser(150)
bot.led(200)
bot.track_frequencies([150,200])
bot.retina(True)

record = True
learn = 's2'

old_vision_state = None

learn_weight = 0
if learn is not False:
    learn_weight = 0.75


model = nengo.Network()
with model:
    motor_gain = 0.3

    def motor_func(t, x):
        bot.motor(x[0] * motor_gain, x[1] * motor_gain, msg_period=0.01)
        return x

    motor = nengo.Node(motor_func, size_out=2, size_in=2)

    def vision_state(t):
        x, y, c = bot.get_frequency_info(0)
        x2, y2, c2 = bot.get_frequency_info(1)

        global old_vision_state
        if old_vision_state is None:
            old_vision_state = x, y

        dx = (x - old_vision_state[0]) * 0
        dy = (y - old_vision_state[1]) * 0

        old_vision_state = x, y

        if c > 1.0:
            c = 1.0
        if c2 > 1.0:
            c2 = 1.0
        return x, y, c, x2, y2, c2
    vision = nengo.Node(vision_state, size_out=6)

    state = nengo.Ensemble(600, 6, radius=2.5)
    nengo.Connection(vision, state)

    action_cfg = nengo.Config()
    action_cfg.configures(nengo.Ensemble)
    action_cfg.configures(nengo.Node)
    action_cfg.configures(nengo.Connection)
    action_cfg[nengo.Ensemble].update(dict(
        encoders=nengo.utils.distributions.Choice([[1]]),
        intercepts=nengo.utils.distributions.Uniform(0, 0.9)))
    with action_cfg:
        actions = nengo.networks.EnsembleArray(n_neurons=50, n_ensembles=5)

    nengo.Connection(state, actions.input[0],
                     function=lambda x: 1.0 if x[1] < -0.85 else 0,
                     transform=1-learn_weight)
    nengo.Connection(actions.output[0], motor, transform=[[-1], [1]])

    nengo.Connection(state, actions.input[1],
                     function=lambda x: 1.0 if x[1] < -0.85 else 0,
                     transform=1-learn_weight)
    nengo.Connection(actions.output[1], motor, transform=[[1], [-1]])

    nengo.Connection(state, actions.input[2],
                     function=lambda x: 1.0 if x[1] > -0.66 else 0,
                     transform=1-learn_weight)
    nengo.Connection(actions.output[2], motor, transform=[[1], [1]])

    nengo.Connection(state, actions.input[3],
                     function=lambda x: 1.0 if x[1] < -0.86 else 0,
                     transform=1-learn_weight)
    nengo.Connection(actions.output[3], motor, transform=[[-1], [-1]])

    nengo.Connection(state, actions.input[4],
                     function=lambda x: 1.0 if x[2] <= 0 else 0,
                     transform=1-learn_weight)
    nengo.Connection(actions.output[4], motor, transform=[[-1], [-1]])

    def print_state(t, x):
        return
        print 'state', ' '.join(['%6.2f' % xx for xx in x])
    nengo.Connection(state, nengo.Node(print_state, size_in=6), synapse=0.01)
    def print_actions(t, x):
        #return
        print t, 'action', ' '.join(['%6.2f' % xx for xx in x])
    nengo.Connection(actions.output, nengo.Node(print_actions, size_in=5),
            synapse=0.01)

    nengo.Connection(actions.ensembles[0], actions.ensembles[1], transform=-5)
    nengo.Connection(actions.ensembles[1], actions.ensembles[0], transform=-5)


    scale = -1.5
    #nengo.Connection(state[4], actions.ensembles[0], transform=-scale)
    #nengo.Connection(state[4], actions.ensembles[1], transform=scale)

    noise = nengo.Node(nengo.utils.functions.whitenoise(0.1, 10, rms=0.05,
                                                       dimensions=2))
    nengo.Connection(noise, actions.input[:2])

    pAction = nengo.Probe(actions.output, synapse=0.03)
    pState = nengo.Probe(state, synapse=0.03)
    pMotor = nengo.Probe(motor, synapse=None)

    if learn is not False:
        states = []
        acts = []
        for fn in os.listdir('.'):
            if fn.startswith('data.bot_choose ') and learn in fn:
                db = shelve.open(fn)
                states.extend(db['state'])
                acts.extend(db['action'])
                db.close()
        #acts = [list(aa) for aa in acts]
        #states = [list(ss) for ss in states]
        tf = nengo.utils.connection.target_function(
                states, acts)
        nengo.Connection(state, actions.input, function=tf['function'],
                eval_points=tf['eval_points'], transform=learn_weight)




sim = nengo.Simulator(model)
if record:
    sim.run(1.5)
else:
    sim.run(1000)


if record:
    fn = 'data.bot_choose %s.dat' % time.asctime()
    fn = fn.replace(':', '-')
    print fn
    db = shelve.open(fn)
    db['state'] = sim.data[pState]
    db['action'] = sim.data[pAction]
    db['motor'] = sim.data[pMotor]
    db.close()

