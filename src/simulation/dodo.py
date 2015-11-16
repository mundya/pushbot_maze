from accuracy import AccuracySim

import numpy as np
import ctn_benchmark

def task_runsim():
    def run():
        rng = np.random.RandomState()

        for seed in range(50, 100):
            strength = rng.uniform(0, 1)
            for n_training in [1, 5, 10, 20]:
                AccuracySim().run(seed=seed, strength=strength, n_training=n_training,
                        n_neurons=1000, D=6, T=6, stim='random', data_dir='accuracy')
    return dict(actions=[run], verbosity=2)

def task_plot():
    def plot():

        datasets = []
        import pylab
        for n_training in [1, 5, 10, 20]:
            data = ctn_benchmark.Data('accuracy')
            for d in data.data[:]:
                if d['_n_training'] != n_training:
                    data.data.remove(d)
            datasets.append(data)

            plot = ctn_benchmark.Plot(data)
            plot.vary('_strength', ['dp_norm'], fill_variance=0.1)
            pylab.ylim(0,1)
            pylab.xlim(0,1)
            pylab.title('n_training: %d' % n_training)
            pylab.tight_layout()

        plot = ctn_benchmark.Plot([datasets[0], datasets[3]])
        plot.vary('_strength', ['dp_norm'], fill_variance=0.1)
        pylab.ylim(0,1)
        pylab.xlim(0,1)
        pylab.legend(['n_training: 1', 'n_training: 20'], loc='lower right')
        pylab.tight_layout()



        pylab.show()
    return dict(actions=[plot])
