
''' 
Module PYFIG 
------------  
Module for manipulating windows/figures created using 
pylab or enthought.mayavi.mlab on the windows platform. 

Figure manipulation involves 
maximization, minimization, hiding, closing, stacking or tiling. 

This module assumes that the figures are uniquely numbered in the following way:
Figure 1
Figure 2
....
or
TVTK scene 1
TVTK scene 2
TVTK scene 3
...

Example
-------
>>> import pylab as p
>>> import pyfig as fig
>>> for ix in range(6): f = p.figure(ix)
>>> fig.stack('all')
>>> fig.stack(1,2)
>>> fig.hide(1)
>>> fig.restore(1)
>>> fig.tile()
>>> fig.pile()
>>> fig.maximize(4)
>>> fig.close('all')
'''