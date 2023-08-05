from graphite import *

# try: 'AI' 'FIG' 'GL' 'GTK' 'PDF' 'PIL' 'PS' 'QD' 'SVG' 'TK' 'VCR' 'WxDc' 'WX'
# For my modified piddle 1.0.15 under Python 2.4 only the following seem to work:
#     'PDF' 'PIL' 'PS'
#     'GL' may work if you get PyOpenGL from http://pyopengl.sourceforge.net/

drawtype = 'PS'   # this is also now a command line parameter (see below)

#----------------------------------------------------------------------
def test1():
	"Copies middle school math lession horizontal bar plot"

	# create a graph
	g = Graph()
	g.title = Text('<b>How Good are Middle School Math Lessons?</b>',
			pos=(0.5, 1.1, 0))
	g.bottom = g.bottom + 40
	g.top = g.top + 40

	# Japanese percent goodness
	g.datasets.append( Dataset([(39,3), (49,2), (9,1)]) )
	# German percent goodness
	g.datasets.append( Dataset([(27,3), (38,2), (35,1)]) )
	# United States percent goodness
	g.datasets.append( Dataset([(0,3), (9,2), (87,1)]) )
	
	g.axes[X].range = [0,100]
	g.axes[X].label = Text('Percent', pos=(0, -0.1, 0))
	xticks = TickMarks()
	xticks.spacing = 20
	xticks.labels = "%d"
	g.axes[X].tickMarks = [xticks]
	
	g.axes[Y].range = [0,4]
	g.axes[Y].label = Text('', pos=(0, -0.1, 0))	# no Y label
	yticks = TickMarks()
	yticks.spacing = 1
	#yticks.offset = 1	# not implemented so I have to start my range at 0
	yticks.labels = ['','Low quality', 'Medium quality', 'High quality']
	yticks.labeldist = -0.14
	g.axes[Y].tickMarks = [yticks]
			
	purplebars = BarPlot()
	purplebars.axis = X
	purplebars.fillStyle = colors.purple
	purplebars.size[Y] = 0.25
	purplebars.shift = (0,0.25,0)

# can easily change to point plot if desired
#	purplebars = PointPlot()
#	purplebars.lineStyle = LineStyle(color=colors.purple)

	redbars = BarPlot()
	redbars.axis = X
	redbars.fillStyle = colors.red
	redbars.size[Y] = 0.25
	redbars.shift = (0,0,0)

	bluebars = BarPlot()
	bluebars.axis = X
	bluebars.fillStyle = colors.blue
	bluebars.size[Y] = 0.25
	bluebars.shift = (0,-0.25,0)

	g.formats = [purplebars, redbars, bluebars]
	
	##### the legend, doing it by hand
	
	# purple box
	g.overlays.append( Box((0.65,0.5,0),(0.68,.55,0),fillStyle=colors.purple) )
	g.overlays.append( Text('Japan',pos=(0.70,0.50,0),
			style=TextStyle(hjust=LEFT,vjust=BOTTOM,font=Font(size=10) ) ) )

	# red box
	g.overlays.append( Box((0.65,0.4,0),(0.68,.45,0),fillStyle=colors.red) )
	g.overlays.append( Text('Germany',pos=(0.70,0.40,0),
			style=TextStyle(hjust=LEFT,vjust=BOTTOM,font=Font(size=10) ) ) )

	# blue box
	g.overlays.append( Box((0.65,0.3,0),(0.68,.35,0),fillStyle=colors.blue) )
	g.overlays.append( Text('United States',pos=(0.70,0.30,0),
			style=TextStyle(hjust=LEFT,vjust=BOTTOM,font=Font(size=10) ) ) )

	# not sure why this is needed to fit it into TK window,
	# but it seems to do the trick
	g.bottom = g.bottom - 30
	g.left = g.left + 10
	return g
	
#----------------------------------------------------------------------

# optional command line argument specified drawtype
import sys
if len(sys.argv) > 1:
	drawtype = sys.argv[1]

# run the tests (keep the graphs and canvases)
g1 = test1()
can1 = genOutput(g1,drawtype,canvasname='graphb')

# if the draytype is interactive, service the canvases
# so users can admite them
if can1.isInteractive():
	can1.serviceCanvas()
