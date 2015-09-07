import nengo

model = nengo.Network()
with model:
    stimulus = nengo.Node(lambda t: 1.1 - t)

    a = nengo.Ensemble(500, 1)

    nengo.Connection(stimulus, a)

    output = nengo.Node(lambda t, x: x, size_in=1)
    nengo.Connection(a, output, function=lambda x: 1 if x > -0.6 else 0)

    p_stim = nengo.Probe(stimulus, synapse=0.03)

    p_output = nengo.Probe(output, synapse=0.03)

sim = nengo.Simulator(model)
sim.run(2.1)

import pylab
pylab.figure(figsize=(6,3))
pylab.axes((0.15, 0.2, 0.8, 0.75))

import numpy as np
stim = np.linspace(-1, 1, 100)
pylab.plot(stim, np.where(stim > -0.6, 1, 0), color='#888888', linewidth=2, label='ideal')

pylab.plot(sim.data[p_stim][100:], sim.data[p_output][100:], color='k', label='neural')

pylab.xlabel('laser.y')
pylab.ylabel('S[0]')

pylab.legend(loc='best')

pylab.savefig('smoothing.png', dpi=600)

pylab.show()
