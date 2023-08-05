from pylab import *
from matplotlib.collections import LineCollection
from matplotlib.colors import ColorConverter
colorConverter = ColorConverter()

# In order to efficiently plot many lines in a single set of axes,
# Matplotlib has the ability to add the lines all at once. Here is a
# simple example showing how it is done.

x = arange(200)
# Here are many sets of y to plot vs x
ys = [x+i for i in x]

# We need to set the plot limits, the will not autoscale
ax = axes()
ax.set_xlim((amin(x),amax(x)))
ax.set_ylim((amin(amin(ys)),amax(amax(ys))))

# colors is sequence of rgba tuples
# linestyle is a string or dash tuple. Legal string values are
#          solid|dashed|dashdot|dotted.  The dash tuple is (offset, onoffseq)
#          where onoffseq is an even length tuple of on and off ink in points.
#          If linestyle is omitted, 'solid' is used
# See matplotlib.collections.LineCollection for more information
line_segments = LineCollection([zip(x,y) for y in ys], # Make a sequence of x,y pairs
                                linewidths    = (0.5,1,1.5,2),
                                colors        = [colorConverter.to_rgba(i) \
                                                 for i in ('b','g','r','c','m','y','k')],
                                linestyle = 'solid')
ax.add_collection(line_segments)
show()


