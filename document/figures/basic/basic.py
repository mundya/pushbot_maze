import pylab
import numpy as np

import plotter

p = plotter.Plotter()
p.load_data(filter='(left)|(right)')
p.compute('turn', lambda data: data['motor'][:,:,0] - data['motor'][:,:,1])
p.compute('speed', lambda data: data['motor'][:,:,0] + data['motor'][:,:,1])

pylab.figure(figsize=(6,6))
pylab.axes((0.2, 0.55, 0.75, 0.4))
p.plot('speed')
pylab.ylabel('speed\nM[left] + M[right]')
pylab.axes((0.2, 0.1, 0.75, 0.4))
p.plot('turn')
pylab.ylabel('rotation\nM[left] - M[right]')
pylab.xlabel('time (s)')

pylab.savefig('basic.png', dpi=600)
pylab.show()
