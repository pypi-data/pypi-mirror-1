######################################################################
# blittergraph.py
#
# This is example was written before utility.py.  In fact
# most of the functions in utility.py were taken from this example.
######################################################################
import string
import Num
from graphite import *

def num(s, errval=0):
	"convert string s to a number; if unable, return errval instead"
	try:
		return float(s)
	except ValueError:
		return errval


def loadTable(fname, delim='\t'):
	file = open(fname,'r')
	data = []
	line = file.readline()
	while line:
		data.append( map(num,string.split(line,delim)) )
		line = file.readline()
	return Num.array(data)


def row(table, rownum):
	return table[rownum]


def col(table, colnum):
	try:
		out = table[:,colnum]
	except IndexError:
		# if it's not a Num array, we have to extract the column the hard way...
		l = len(table)
		out = Num.zeros((l,), Num.Float)
		for i in range(l):
			out[i] = table[i][colnum]
	return out


def addplotY(graph,ydata,lineStyle=UNSPECIFIED,symbol=UNSPECIFIED,symbolStyle=UNSPECIFIED):
	data = Dataset()
	data.y = ydata
	data.x = range(0,len(ydata))		# PATCH just for testing!
	graph.datasets.append( data )
	setnum = len(graph.datasets) - 1
	format = PointPlot(lineStyle=lineStyle,symbol=symbol,symbolStyle=symbolStyle)
	if setnum >= len(graph.formats):
		graph.formats.append(format)
	else:
		graph.formats[setnum] = format

def addLegend(g, colors, names, x=0.1, y=0.8):
	"add a legend, using colors only (no symbols or line styles)"
	for i in range(len(names)):
		color = colors[i%len(colors)]
		# add the box
		g.overlays.append( Box((x,y,0),(x+0.04,y+0.06,0),fillStyle=color) )
		# add the text
		g.overlays.append( Text(names[i],pos=(x+0.06,y+0.03,0),
				style=TextStyle(hjust=LEFT,vjust=CENTER,font=Font(size=10))) )
		# move to text item
		y = y - 0.08

# load the data
data = loadTable('blitter.dat')

# define the colors and names for the data sets
colors = colors.red, colors.green, colors.blue, (colors.red+colors.yellow)/3
names = "CopyBits", "Direct", "DirectMem", "RAVE"

# create the graph, and add the plots
g = Graph()
addplotY(g, col(data,4), LineStyle(color=colors[0], width=2), symbol=None)
addplotY(g, col(data,5), LineStyle(color=colors[1], width=2), symbol=None)
addplotY(g, col(data,6), LineStyle(color=colors[2], width=2), symbol=None)
addplotY(g, col(data,7), LineStyle(color=colors[3], width=2), symbol=None)

# set up axes
g.axes[X].range = (0,len(data))
g.axes[Y].range = (0,1000)
xticks = TickMarks(spacing=1)
xticks.inextent = xticks.outextent = 0
xticks.labels = map(lambda x:("%d" % x)[:10*(x!=0)], col(data,3)) + ['']
g.axes[X].tickMarks = [xticks]
g.axes[X].label.text = "Problem Size"

yticks = TickMarks(spacing=250)
yticks.labels = "%d"
g.axes[Y].tickMarks = [yticks]
g.axes[Y].label.text = "Frames Per Second"

# finally, let's add a legend
addLegend(g,colors,names)

genOutput(g,'PDF',canvasname='blittergraph.pdf')
