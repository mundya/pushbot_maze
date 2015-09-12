import nengo
import numpy as np

model = nengo.Network()
with model:
    stim = nengo.Node(0)

    ens = nengo.Ensemble(n_neurons=1, dimensions=1,
                         encoders=[[1]],
                         intercepts=[-0.5],
                         max_rates=[50])

    nengo.Connection(stim, ens, synapse=None)

    p_voltage = nengo.Probe(ens.neurons, 'voltage')
    p_spikes = nengo.Probe(ens.neurons)
    p_output = nengo.Probe(ens, synapse=0.05)

dt = 0.001
sim = nengo.Simulator(model, dt=dt)
sim.run(0.2)

import pylab
pylab.figure(figsize=(6,4))
pylab.subplot(2, 1, 1)
pylab.plot(sim.trange(), sim.data[p_voltage], drawstyle='steps')
pylab.vlines(sim.trange()[np.where(sim.data[p_spikes] > 0)[0]]-dt/2, 0, 2, lw=2, color='k')
pylab.xlim(0, 0.2)
pylab.yticks([])
pylab.hlines([1.0], 0, 0.2, color='#888888', linestyles='dashed')
pylab.ylabel('voltage\nand activity')
pylab.subplot(2, 1, 2)
pylab.plot(sim.trange(), sim.data[p_output], drawstyle='steps')
pylab.yticks([])
pylab.ylabel('synaptic\noutput')
pylab.xlabel('time (s)')
pylab.xlim(0, 0.2)
pylab.tight_layout()
pylab.savefig('neuron.png', dpi=300)
pylab.show()
