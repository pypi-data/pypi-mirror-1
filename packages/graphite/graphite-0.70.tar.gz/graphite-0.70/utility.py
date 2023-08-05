"""
Module Utility
This module contains the various utility function which are used with
the Graphite plotting package. 

Public Functions (functions which a graphite user will directly call):

	genOutput(graph,backend): generate the graph with one of
		the supported backends, 'PDF', 'PS', 'PIL', etc
		with the proper size?

Design: Frequently needed functions which shouldn't really be members
of the Graph class or other related classes to facilitate later change.

To Do:
"""

#------------------------------------------------------
import colors


_cm = {}
for (k, v) in colors.__dict__.items():
	if isinstance(v, colors.Color) and type(k)==type(''):
		_cm[k] = v

SC = 256
FS = float(SC)

def _hs(s):
	r = (hash('red%s' % s)/3) % SC
	g = (hash('green%s' % s)/5) % SC
	b = (hash('blue%s' % s)/7) % SC
	return colors.Color(r/FS, g/FS, b/FS)


def getcolor(s):
	"""This gets you a color from any random text.  If the text is
	a color name or a i,j,k triple, then it's a non-random color.
	Otherwise, it's just random."""
	try:
		return _cm[s]
	except KeyError:
		pass

	a = s.strip().split(',')
	if len(a) == 3:
		try:
			r = float(a[0])
			g = float(a[1])
			b = float(a[2])
		except ValueError:
			return _hs(s)
		if 0.0<=r<FS and 0<=g<FS and 0<=b<FS:
			return colors.Color(r/FS, g/FS, b/FS)
	return _hs(s)


#----------------------------------------------------------------------

import pid as PID
def genOutput(graph, backend, size=(400,300), canvasname="graph"):
	"""Size sets the overall size of the plot.  It takes a tuple,
	measured in pixels.
	Backend specifies the output file format, such as 'PS', or 'PDF'.
	Graph is the graph to be produced, and
	canvasname specifies the title (for the GUI) or the filename.
	"""
	# import the relevant module
	backend = 'piddle%s' % backend
	if not hasattr(PID, backend):
		print "Graphite_ERR: The backend you want (%s) is not available in graphite." % backend
		print "Normally, PS, PDF, SVG, TK, WX, and PIL are available, if your python supports everything."
		print "PIL, TK and WX are installation-dependent."
		raise ImportError, "Can not import %s" % backend

	module = getattr(PID, backend)

	# figure out the canvas class name (e.g., "PILCanvas") and get that
	canvasClass = getattr(module, backend[6:]+"Canvas")

	# create canvas
	if backend == 'piddleVCR':
		canvas = canvasClass(size, canvasname, playthru=PID.piddlePS.PSCanvas(size))	
	else:
		canvas = canvasClass(size, canvasname)
        

	# draw the graph
	graph.draw(canvas)

	# do post-test cleanup
	canvas.flush()
	if backend == 'piddlePIL':
		filename = canvas.name + ".png"
		canvas.save(filename)
		print filename, "graph saved to ", filename
	elif backend == 'piddleVCR':
		filename = canvas.name + ".vcr"
		canvas.save(filename)
		print filename, "graph saved to ", filename
	elif canvas.isInteractive():
		pass
	else:
		canvas.save()

        return canvas
