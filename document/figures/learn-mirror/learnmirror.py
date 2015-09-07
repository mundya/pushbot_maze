import pylab
import numpy as np

import plotter

p = plotter.Plotter()
p.load_data(filter='learn1n')
p.compute('turn', lambda data: data['motor'][:,:,1] - data['motor'][:,:,0])

pylab.figure(figsize=(6,6))
pylab.axes((0.2, 0.55, 0.75, 0.4))
p.plot('turn')
pylab.ylabel('without mirror\nrotation\nM[left] - M[right]')


p = plotter.Plotter()
p.load_data(filter='learn1m')
p.compute('turn', lambda data: data['motor'][:,:,1] - data['motor'][:,:,0])

pylab.axes((0.2, 0.1, 0.75, 0.4))
p.plot('turn')
pylab.ylabel('with mirror\nrotation\nM[left] - M[right]')
pylab.xlabel('time (s)')

pylab.savefig('learnmirror.png', dpi=600)
pylab.show()
