import nengo
import nengo.utils.functions

model = nengo.Network()
with model:

    def vision(t):
        if t % 0.2 < 0.1:
            return [0, 0, 1.0]
        else:
            return [0, -0.8, 1.0]

    state = nengo.Ensemble(300, 3, radius=1.7)
    nengo.Connection(nengo.Node(vision), state)

    action_cfg = nengo.Config()
    action_cfg.configures(nengo.Ensemble)
    action_cfg.configures(nengo.Node)
    action_cfg.configures(nengo.Connection)
    action_cfg[nengo.Ensemble].update(dict(
        encoders=nengo.utils.distributions.Choice([[1]]),
        intercepts=nengo.utils.distributions.Uniform(0, 0.9)))
    with action_cfg:
        actions = nengo.networks.EnsembleArray(n_neurons=50, n_ensembles=2)

    nengo.Connection(state, actions.input[0],
                     function=lambda x: 1.0 if x[1] < -0.6 else 0)

    nengo.Connection(state, actions.input[1],
                     function=lambda x: 1.0 if x[1] < -0.6 else 0)

    def print_state(t, x):
        pass
        #print 'state', ' '.join(['%1.2f' % xx for xx in x])
    nengo.Connection(state, nengo.Node(print_state, size_in=3), synapse=0.01)
    def print_actions(t, x):
        pass
        #print 'action', ' '.join(['%1.2f' % xx for xx in x])
    nengo.Connection(actions.output, nengo.Node(print_actions, size_in=2),
            synapse=0.01)

    nengo.Connection(actions.ensembles[0], actions.ensembles[1], transform=-5)
    nengo.Connection(actions.ensembles[1], actions.ensembles[0], transform=-5)

    noise = nengo.Node(nengo.utils.functions.whitenoise(0.1, 10, rms=0.05,
                                                       dimensions=2))
    nengo.Connection(noise, actions.input)

    pAction = nengo.Probe(actions.output, synapse=0.03)
    pState = nengo.Probe(state, synapse=0.03)


sim = nengo.Simulator(model)
sim.run(5)

import pylab
pylab.subplot(2,1,1)
pylab.plot(sim.trange(), sim.data[pState])

pylab.subplot(2,1,2)
pylab.plot(sim.trange(), sim.data[pAction])

pylab.show()
