import shelve
import os
import re

import pylab
import numpy as np
import scipy.ndimage.filters

class Plotter(object):
    def __init__(self, dt=0.003, sigma=0.15):
        self.data = {}
        self.dt = dt
        self.sigma_steps = int(sigma / dt)

    def load_data(self, filter='', dir='.'):
        for fn in os.listdir(dir):
            if fn.startswith('data.bot_choose ') and re.search(filter, fn):
                db = shelve.open(fn)
                for k in db.keys():
                    if k not in self.data:
                        self.data[k] = []
                    self.data[k].append(db[k])
                db.close()
        for k in self.data.keys():
            self.data[k] = np.array(self.data[k])

    def compute(self, name, function):
        self.data[name] = function(self.data)

    def smooth(self, name):
        return scipy.ndimage.filters.gaussian_filter(self.data[name],
            sigma=(0, self.sigma_steps), mode='nearest')

    def smooth_ci(self, name, bin_size=10, stat=np.mean, samples=500, p=0.95):
        limit = int(samples * (1 - p) / 2)
        data = self.data[name]
        steps = data.shape[1] / bin_size
        r = np.zeros((steps, 2))
        for i in range(steps):
            items = data.shape[0] * bin_size
            dist = i * bin_size + np.random.randn(items, samples) * self.sigma_steps
            dist = np.clip(dist.astype(int), 0, data.shape[1] - 1)
            row = np.random.randint(data.shape[0], size=(items, samples))
            d = data[row, dist]
            values = stat(d, axis=0)
            values = np.sort(values)

            r[i] = values[limit], values[-limit]
        return r

    def plot(self, name, bin_size=10, filename=None):
        ci = self.smooth_ci(name, bin_size)
        runs = self.smooth(name)
        t = np.arange(len(runs[0])) * self.dt
        t_ci = np.arange(len(ci)) * self.dt * bin_size

        pylab.fill_between(t_ci, ci[:,0], ci[:,1], color='black',
                           facecolor='black')

        lines = pylab.plot(t, runs.T, color='#808080')

        lines_area, = pylab.plot([0], [0], color='black', linewidth=10)

        pylab.legend([lines[0], lines_area], ['individual runs', 'mean (95% C.I.)'], loc='best')


        if filename is not None:
            pylab.savefig(filename, dpi=600)







if __name__ == '__main__':
    p = Plotter()
    p.load_data(filter='(left)|(right)')
    #p.load_data(filter='learnL')
    p.compute('turn', lambda data: data['motor'][:,:,0] - data['motor'][:,:,1])
    p.compute('speed', lambda data: np.mean(data['motor'], axis=2))

    pylab.figure()
    p.plot('speed', filename='speed.png')
    pylab.figure()
    p.plot('turn', filename='turn.png')
    pylab.show()
