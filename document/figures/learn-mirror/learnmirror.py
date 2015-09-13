import pylab
import numpy as np

import plotter

p = plotter.Plotter()
p.load_data(filter='learn1n')
p.compute('turn', lambda data: data['motor'][:,:,1] - data['motor'][:,:,0])

pylab.figure(figsize=(6,6))
pylab.axes((0.2, 0.55, 0.75, 0.4))
p.plot('turn')
pylab.ylabel('rotation\nM[left] - M[right]', fontsize=14)
pylab.text(0.5, 0.4, 'without mirror', fontsize=18)


p = plotter.Plotter()
p.load_data(filter='learn1m')
p.compute('turn', lambda data: data['motor'][:,:,1] - data['motor'][:,:,0])

pylab.axes((0.2, 0.1, 0.75, 0.4))
p.plot('turn')
pylab.ylabel('rotation\nM[left] - M[right]', fontsize=14)
pylab.text(0.5, 0.4, 'with mirror', fontsize=18)
pylab.xlabel('time (s)')

pylab.savefig('learnmirror.png', dpi=600)
pylab.show()
