import nstbot


bot = nstbot.pushbot.PushBot()
#bot.connect(connection.Serial('/dev/ttyUSB0', baud=4000000))
bot.connect(nstbot.connection.Socket('10.162.177.135'))

bot.laser(150)
bot.track_frequencies([150])
bot.retina(True)

import nengo

model = nengo.Network()
with model:
    motor_gain = 2
    motor = nengo.Node(lambda t, x: bot.motor(x[0] * motor_gain,
                                              x[1] * motor_gain,
                                              msg_period=0.01),
                       size_in=2)

    vision = nengo.Node(lambda t: bot.get_frequency_info(0), size_out=3)

    state = nengo.Ensemble(300, 3)
    nengo.Connection(vision, state)

    model.config[nengo.Ensemble].encoders = nengo.utils.distributions.Choice([[1]])
    model.config[nengo.Ensemble].intercepts = nengo.utils.distributions.Uniform(0, 0.9)

    Q_fwd = nengo.Ensemble(50, 1)
    nengo.Connection(state, Q_fwd,
                     function=lambda x: 1.0 if x[1] > -0.56 else 0)
    nengo.Connection(Q_fwd, motor, transform=[[0.08], [0.08]])

    Q_back = nengo.Ensemble(50, 1)
    nengo.Connection(state, Q_back,
                     function=lambda x: 1.0 if x[1] < -0.56 else 0)
    nengo.Connection(Q_back, motor, transform=[[-0.06], [-0.06]])

    Q_cant_see = nengo.Ensemble(50, 1)
    nengo.Connection(state, Q_cant_see,
                     function=lambda x: 1.0 if x[2] <= 0 else 0)
    nengo.Connection(Q_cant_see, motor, transform=[[-0.1], [-0.1]])

    Q_avoid_right = nengo.Ensemble(50, 1)
    nengo.Connection(state, Q_avoid_right,
                     function=lambda x: 1.0 if x[1] < -0.4 else 0)
    nengo.Connection(Q_avoid_right, motor, transform=[[0.04], [-0.04]])

    Q_avoid_left = nengo.Ensemble(50, 1)
    nengo.Connection(state, Q_avoid_left,
                     function=lambda x: 1.0 if x[1] < -0.4 else 0)
    nengo.Connection(Q_avoid_left, motor, transform=[[-0.04], [0.04]])

    nengo.Connection(Q_avoid_right, Q_avoid_left, transform=-1)
    nengo.Connection(Q_avoid_left, Q_avoid_right, transform=-1)



sim = nengo.Simulator(model)
sim.run(100)


sim = nengo.Simulator(model)
sim.run(100)
