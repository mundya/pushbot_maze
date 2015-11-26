import ctn_benchmark
import nengo
import numpy as np

class AccuracySim(ctn_benchmark.Benchmark):
    def params(self):
        self.default('number of dimensions', D=1)
        self.default('simulation time', T=6.0)
        self.default('number of neurons', n_neurons=100)
        self.default('synapse', synapse=0.01)
        self.default('stimulus type', stim='ramp')
        self.default('number of training examples', n_training=1)
        self.default('number of bumps', n_bumps=2)
        self.default('signal strength', strength=1.0)

    def model(self, p):
        model = nengo.Network()

        N = int(p.T / p.dt)

        t = np.arange(N) * p.dt
        train_response = np.zeros((N, 1))
        width = 0.2
        train_response[:,0] += np.exp(-(t-p.T*3/4)**2/(2*width**2))
        if p.n_bumps > 1:
            train_response[:,0] += np.exp(-(t-p.T*1/4)**2/(2*width**2))


        if p.stim == 'ramp':
            train_stim = np.zeros((N, p.D))
            if p.n_bumps == 1:
                train_stim[:,0] += np.linspace(-1, 1, N)
            else:
                train_stim[:N/2,0] += np.linspace(-1, 1, N/2)
                train_stim[N/2:,0] += np.linspace(-1, 1, N/2)


            test_sim = train_stim
            test_response = train_response
        elif p.stim == 'random':
            train_stims = []
            train_res = []
            train_fg = np.zeros((N, p.D))
            signal_fg = np.random.normal(size=p.D)
            signal_fg = signal_fg / np.linalg.norm(signal_fg)
            signal_fg *= p.strength
            for i in range(p.n_training + 1):
                train_stim = np.zeros((N, p.D))
                signal_bg = nengo.processes.WhiteSignal(p.T, high=2.0, rms=0.5)
                train_stim = signal_bg.run_steps(N, d=p.D, dt=p.dt)

                train_stim += np.outer(train_response, signal_fg)
                train_stims.append(train_stim)
                train_res.append(train_response)


            test_sim = train_stims[0]
            test_response = train_res[0]

            train_stim = np.vstack(train_stims[1:])
            train_response = np.vstack(train_res[1:])




        with model:
            ens = nengo.Ensemble(p.n_neurons, p.D)
            result = nengo.Node(None, size_in=1)
            self.probe_result = nengo.Probe(result, synapse=None)

            self.conn = nengo.Connection(ens, result, synapse=p.synapse,
                             **nengo.utils.connection.target_function(train_stim,
                                                           train_response))

            stim = nengo.Node(lambda t: test_sim[int(t / p.dt) % N])
            nengo.Connection(stim, ens, synapse=None)
            self.probe_stim = nengo.Probe(stim, synapse=None)

            ideal_result = nengo.Node(lambda t: test_response[int(t/p.dt)%N])
            self.probe_ideal = nengo.Probe(ideal_result, synapse=None)


        return model

    def evaluate(self, p, sim, plt):
        sim.run(p.T)
        self.record_speed(p.T)

        if plt:
            plt.subplot(2, 1, 1)
            plt.plot(sim.trange(), sim.data[self.probe_stim])
            plt.ylabel('stimulus')
            plt.subplot(2, 1, 2)
            plt.plot(sim.trange(), sim.data[self.probe_result], label='result')
            plt.plot(sim.trange(), sim.data[self.probe_ideal], lw=2, label='ideal')
            plt.legend(loc='upper left')
            ylabel = 'action strength\nwith %d training example%s' % (
                            p.n_training, 's' if p.n_training>1 else '')
            plt.ylabel(ylabel)
            plt.ylim(-0.2, 1.2)
            plt.xlabel('time (s)')

        rmse_train = sim.data[self.conn].solver_info['rmses']
        diff = sim.data[self.probe_result] - sim.data[self.probe_ideal]
        rmse_test = np.sqrt(np.mean(diff**2))

        dp = np.dot(sim.data[self.probe_result][:,0], sim.data[self.probe_ideal][:,0])
        dp = dp / np.linalg.norm(sim.data[self.probe_result])
        dp = dp / np.linalg.norm(sim.data[self.probe_ideal])
        if plt:
            plt.text(p.T/2, 0.9, 'Similarity: %1.3f' % dp, ha='center')

        return dict(rmse_train=rmse_train[0], rmse_test=rmse_test, dp_norm=dp)


if __name__ == '__main__':
    AccuracySim().run()





