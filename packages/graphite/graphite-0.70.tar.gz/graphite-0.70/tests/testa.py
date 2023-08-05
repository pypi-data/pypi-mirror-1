from graphite import *

# try: 'AI' 'FIG' 'GL' 'GTK' 'PDF' 'PIL' 'PS' 'QD' 'SVG' 'TK' 'VCR' 'WxDc' 'WX'
# For my modified piddle 1.0.15 under Python 2.3 only the following seem to work:
#     'PDF' 'PIL' 'PS'
#     'GL' may work if you get PyOpenGL from http://pyopengl.sourceforge.net/

drawtype = 'PS'   # this is also now a command line parameter (see below)

#----------------------------------------------------------------------
def test1():
	"Tests clipping, axis labels, tickmark labels, and secondary Y axis."

	# create a graph
	g = Graph()
	
	# change the position of the graph on the canvas
	g.left = 60
	g.top = 70
	g.bottom = 240
	
	# put a title on this graph
	g.title = Text('<b><u>Sample Graph Title</u></b>')

	# append some data, and set the line styles
	g.datasets.append( Dataset([(0.1,0.3), (0.4,0.8), (0.7,0.7), (0.8,0.4)]) )
	redplot = PointPlot()
	redplot.lineStyle.color = colors.red
	redplot.lineStyle.width = 2
	redplot.lineStyle.kind = DASHED
	redplot.symbol = None
	g.formats = [redplot]
	
	g.datasets.append( Dataset([(0.1,1.2), (0.5,0.8), (0.9,0.7)]) )
	g.formats.append( PointPlot(LineStyle(width=3, color=colors.green)) )

	g.datasets.append( Dataset([(0.1,0,0), (0.5,0,1), (1,0,0)]) )
	g.formats.append( PointPlot(LineStyle(width=3, color=colors.purple)) )
	g.axes[2].range = [0,1]

	# adjust the Y axis range and tickmarks
	g.axes[1].range = [0,1.5]
	g.axes[1].tickMarks = [ \
#			TickMarks(inextent=1, spacing=0.5, lineStyle=LineStyle(color=colors.medgray)), \
			TickMarks(inextent=1, spacing=0.5, lineStyle=LineStyle(color=colors.gray)), \
			TickMarks()	\
		]
#	g.axes[1].drawPos.append( ((1,0,0),(1,1,0)) )

	# create a second Y axis for our other line
	newaxis = Axis('Y')
	# put it over on the right
	newaxis.drawPos = [ ((1,0,0),(1,1,0)) ]
	# give it a different label
	newaxis.label = Text('Second Y Axis (&Theta;)',angle=-90,pos=(.1,0,0))
	# set its range
	newaxis.range = [0,1]
	g.axes.append(newaxis)
	
	g.axes[0].tickMarks[0].labels = AUTO
	g.axes[1].tickMarks[0].labels = AUTO

	#g.eyePosition = (0.5, 1.3, -5)
	#g.perspective = 1

	g.axes[X].range = [0.2,0.8]
	g.axes[Y].range = [0.5,1.0]
#	g.axes[0].logbase = 10

	return g

#----------------------------------------------------------------------
def spiral(g, steps=100):
	"add a sprial and two shadows to the graph"
	t0, t1 = 0, 1
	tstep = float(t1-t0)/steps

	from math import sin, cos
	n = int((t1-t0)/tstep)
	data = [0]*n
	t = t0
	for i in range(n):
		data[i] = (t*cos(t*40), t, t*sin(t*40))
		t = t + tstep

	g.datasets.append( Dataset(map(lambda d:(d[0],0,d[2]),data)) )
	g.datasets.append( Dataset(map(lambda d:(-1,d[1],d[2]),data)) )
	g.datasets.append( Dataset(data) )


def test2():
	"tests 3D line plot, perspective, and computation time"

	# create a graph
	g = Graph()

	# append some data, and set the line styles
	spiral(g, steps=200)

	g.formats[0].lineStyle.color = colors.purple
	g.formats[0].lineStyle.width = 2
	g.formats[0].symbol = None

	g.formats.append( PointPlot(LineStyle(width=2, color=colors.green)) )
	g.formats.append( PointPlot(LineStyle(width=2, color=colors.red)) )
	g.formats[1].symbol = g.formats[2].symbol = None
	
	g.eyePosition = (1, 1.3, -5)
	g.perspective = 1
	
	g.axes[X].range = [-1,1]
	g.axes[X].label = None
	
	g.axes[Y].range = [0,1]
	g.axes[Y].label = None

	g.axes[Z].range = [-1,1]

	# not sure why this is needed to fit it into TK window,
	# but it seems to do the trick
	g.bottom = g.bottom - 40
	g.left = g.left + 20
	
	return g


#----------------------------------------------------------------------
def test3():
	"tests a simple vertical bar plot"

	# create a graph
	g = Graph()

	g.datasets.append( Dataset([(1,0.4), (2,1.3), (3,0.8)]) )
	g.datasets.append( Dataset([(1,0.2), (2,0.95), (3,0.75)]) )
	
	g.axes[X].range = [0,4]
	g.axes[X].tickMarks[0].spacing = 1
		
	gridlines = TickMarks(inextent=1, spacing=0.5, lineStyle=LineStyle(color=colors.gray))
	smallticks = TickMarks(spacing=0.2)
	smallticks.labels = AUTO
	g.axes[Y].tickMarks = [ gridlines, smallticks ]
	g.axes[Y].range = [0,1.5]

	g.axes[Z].tickMarks = []
	
	greenbars = BarPlot()
	greenbars.base = 0.5
	greenbars.fillStyle = colors.green
	greenbars.size[X] = 0.4
	greenbars.shift = (-0.2,0,0)

	bluebars = BarPlot()
	bluebars.base = 0.5
	bluebars.fillStyle = (colors.blue + colors.white)/2
	bluebars.size[X] = 0.4
	bluebars.shift = (0.2,0,0)

	g.formats = [greenbars, bluebars]

	return g

#----------------------------------------------------------------------
def test4():
	"tests a horizontal bar plot, string tickmark labels"
	# NOTE: right side of frame is currently overplotted by a grid line;
	# that should go away when z-sorting is implemented
	
	# create a graph
	g = Graph()

	g.datasets.append( Dataset([(0.4,1), (1.3,2), (0.8,3)]) )
	g.datasets.append( Dataset([(0.2,1), (0.95,2), (0.75,3)]) )
	
	g.axes[X].range = [0,1.5]		
	gridlines = TickMarks(inextent=1, spacing=0.5, lineStyle=LineStyle(color=colors.gray))
	smallticks = TickMarks(spacing=0.25)
	smallticks.labels = "%4.2f"		# total width=4, precision=2
	g.axes[X].tickMarks = [ gridlines, smallticks ]

	g.axes[Y].range = [0,4]
	yticks = g.axes[Y].tickMarks[0]
	yticks.spacing = 1
	yticks.labels = ['', 'Uno', 'Dos', 'Tres']

	greenbars = BarPlot()
	greenbars.axis = X
	greenbars.fillStyle = colors.green
	greenbars.size[Y] = 0.2
	greenbars.shift = (0,-0.1,0)

	bluebars = BarPlot()
	bluebars.axis = X
	bluebars.fillStyle = (colors.blue + colors.white)/2
	bluebars.size[Y] = 0.2
	bluebars.shift = (0,0.1,0)
	g.formats = [greenbars, bluebars]
	
	return g

#----------------------------------------------------------------------
def test5():
	"A complex multi-part graph."

	# create a graph
	g = Graph()

	# append some data, and set the line styles
	g.datasets.append( Dataset([(0.1,0.3), (0.4,0.8), (0.7,0.7), (0.8,0.4)]) )
	g.formats[0].lineStyle.color = colors.red
	g.formats[0].lineStyle.width = 2

	g.datasets.append( Dataset([(0.1,1.2), (0.5,0.8), (0.9,0.7)]) )
	g.formats.append( PointPlot(LineStyle(width=3, color=colors.green)) )

	# adjust the Y axis range and tickmarks
	g.axes[Y].range = [0,1.5]

	# shrink the X axis down to just the left 1/3
	g.axes[X].drawPos = [ ((0,0,0),(0.6,0,0)) ]

	# create a second X axis the right part of the graph
	newaxis = Axis('X')
	# put it over on the right
	newaxis.drawPos = [ ((0.66,0,0),(1,0,0)) ]
	# give it a different label
	newaxis.label.text = 'Second X'
	# set its range
	newaxis.range = [0,1]
	newaxis.tickMarks[0].labels = AUTO
	newaxis.tickMarks[0].spacing = 0.5
	g.axes.append(newaxis)
	
	g.axes[X].tickMarks[0].labels = AUTO
	g.axes[Y].tickMarks[0].labels = AUTO

	g.axes[X].range = [0.2,0.8]
	g.axes[Y].range = [0.5,1.0]

	return g

#----------------------------------------------------------------------
def test6():
	"a vertical 3D bar plot"

	# create a graph
	g = Graph()

	g.datasets.append( Dataset([(1,0.4), (2,1.3), (3,0.8)]) )
	g.datasets.append( Dataset([(1,0.2), (2,0.95), (3,0.75)]) )
	
	g.axes[X].range = [0,4]
	ticks = g.axes[X].tickMarks[0]
	ticks.spacing = 1
	ticks.labels = ['',"Spam", "Spam<sub>2</sub>", "Spam<sub>3</sub>",'']
		
	gridlines = TickMarks(inextent=1, spacing=0.5, lineStyle=LineStyle(color=colors.gray))
	smallticks = TickMarks(spacing=0.2)
	smallticks.labels = AUTO
	g.axes[Y].tickMarks = [ gridlines, smallticks ]
	g.axes[Y].range = [0,1.6]

	g.axes[Z].tickMarks = []
	
	greenbars = BarPlot()
	greenbars.fillStyle = colors.green
	greenbars.size[X] = 0.3
	greenbars.shift = (-0.2,0,0.1)

	bluebars = BarPlot()
	bluebars.fillStyle = (colors.blue + colors.white)/2
	bluebars.size[X] = 0.3
	bluebars.shift = (0.2,0,0.1)

	g.formats = [greenbars, bluebars]

	g.eyePosition = (0.9, 1, -5)

	# not sure why this is needed to fit it into TK window,
	# but it seems to do the trick
	g.bottom = g.bottom - 10
	
	return g
#----------------------------------------------------------------------
def test7():
	"a realistic line plot with actual data"
	
	g = Graph()
	g.datasets.append( Dataset([(8,2889920),(16,7472640),(32,12882944),
			(64,16089088),(128,17285120),(256,17825792)]) )

	g.datasets.append( Dataset([(8,2889920),(16,4574464),(32,5566464),
			(64,5857280),(128,5865472),(256,5832704)]) )

	g.datasets.append( Dataset([(8,10154816),(16,10382848),(32,10728448),
			(64,10653696),(128,10665984),(256,10682368)]) )

	g.datasets.append( Dataset([(8,6413184),(16,6313728),(32,6413312),
			(64,6430720),(128,6471680),(256,6422528)]) )


	format0 = PointPlot()
	format0.lineStyle = LineStyle(width=2, color=colors.green, kind=SOLID)
	format0.symbol = CircleSymbol
	ov0 = Text("CopyBits unscaled", pos=(0.7,0.92,0) )
	
	format1 = PointPlot()
	format1.lineStyle = LineStyle(width=2, color=colors.red, kind=SOLID)
	format1.symbol =CircleSymbol
	ov1 = Text("CopyBits scaled", pos=(0.7,0.25,0))
	
	format2 = PointPlot()
	format2.lineStyle = LineStyle(width=2, color=colors.green, kind=DASHED)
	format2.symbol = SquareSymbol
	ov2 = Text("Direct misaligned", pos=(0.7,0.38,0))
	
	format3 = PointPlot()
	format3.lineStyle = LineStyle(width=2, color=colors.red, kind=DASHED)
	format3.symbol = SquareSymbol
	ov3 = Text("Direct aligned", pos=(0.7,0.58,0))

	g.formats = [format0, format1, format2, format3]	
	g.overlays = (ov0, ov1, ov2, ov3)

	g.axes[X].range = [0,256]
	g.axes[X].tickMarks[0].spacing = 64
	g.axes[X].tickMarks[0].labels = "%d"
	g.axes[X].label.text = "Output Width (pixels)"
	
	g.axes[Y].range = [0,2E7]
	g.axes[Y].tickMarks[0].spacing = 0.5E7
	g.axes[Y].tickMarks[0].labels = \
		lambda n,x:"%d" % (x/1e6)
	g.axes[Y].label.text = "10<super>6</super> pixels/sec"

	g.title.text = "<b>Blitter Speed Comparison</b>"

	# not sure why this is needed to fit it into TK window,
	# but it seems to do the trick
	g.top = g.top + 20

	return g
	
#----------------------------------------------------------------------
#----------------------------------------------------------------------

# optional command line argument specified drawtype
import sys
if len(sys.argv) > 1:
	drawtype = sys.argv[1]

# run the tests (keep the graphs and canvases)
g1 = test1()
can1 = genOutput(g1,drawtype, canvasname='graph1')
g2 = test2()
can2 = genOutput(g2,drawtype, canvasname='graph2')
g3 = test3()
can3 = genOutput(g3,drawtype, canvasname='graph3')
g4 = test4()
can4 = genOutput(g4,drawtype, canvasname='graph4')
g5 = test5()
can5 = genOutput(g5,drawtype, canvasname='graph5')
g6 = test6()
can6 = genOutput(g6,drawtype, canvasname='graph6')
g7 = test7()
can7 = genOutput(g7,drawtype, canvasname='graph7')

# if the drawtype is interactive, service the canvases
# so users can admite them
if can1.isInteractive():
	can1.serviceCanvas()
