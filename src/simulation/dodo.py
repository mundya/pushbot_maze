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

def task_runsimgrid():
    def run():
        rng = np.random.RandomState()

        for seed in range(0, 150):
            for strength in [0, 0.5, 1.0, 1.5, 2.0]:
                for n_training in [50]:#[1, 5, 10, 15, 20]:
                    AccuracySim().run(seed=seed, strength=strength, n_training=n_training,
                        n_neurons=1000, D=6, T=6, stim='random', data_dir='acc_grid')
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
            pylab.xlim(0,2)
            pylab.title('n_training: %d' % n_training)
            pylab.tight_layout()

        plot = ctn_benchmark.Plot([datasets[0], datasets[3]])
        plot.vary('_strength', ['dp_norm'])#, fill_variance=0.1)
        pylab.ylim(0,1)
        pylab.xlim(0,2)
        pylab.legend(['n_training: 1', 'n_training: 20'], loc='lower right')
        pylab.tight_layout()



        pylab.show()
    return dict(actions=[plot])

def task_plot_grid():
    def plot():

        datasets = []
        legend = []
        import pylab
        for n_training in [1, 5, 10, 20, 50]:
            data = ctn_benchmark.Data('acc_grid')
            for d in data.data[:]:
                if d['_n_training'] != n_training:
                    data.data.remove(d)
            datasets.append(data)
            legend.append('training examples: %d' % n_training)

        plot = ctn_benchmark.Plot(datasets)
        plot.lines('_strength', ['dp_norm'], x_offset=0.01)
        pylab.ylim(0,1)
        pylab.xlim(-0.1,2.1)
        pylab.legend(legend, loc='lower right')
        pylab.xlabel('signal strength $|\\alpha|$')
        pylab.ylabel('similarity')
        pylab.axhline(0.3437, ls='dashed', lw=1, c='k')

        pylab.tight_layout()
        pylab.savefig('plot_grid.png', dpi=300)

        pylab.show()
    return dict(actions=[plot])
