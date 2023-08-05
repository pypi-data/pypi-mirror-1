"""Graphite.  See http://graphite.sourceforge.net for information.
"""

# Revisions...
#
#  6/10/99  JJS: fixed bug in Graph.draw which was transforming overlays,
#				causing them to disappear upon a second plotting.
#  6/14/99  JJS: changed default lineStyle and symbol in PointPlot constructor
#               to UNSPECIFIED, and supported UNSPECIFIED symantics
#  9/99     MMS: exportString implemented, automatic tickmark spacing and axis range
#  10/18/99 MMS: implemented labeldist as a TickMarks property
#  2000, 2001 GPK: Misc fixes.  Better integration with Numerical python.
#  2003 GPK: Cleanup, better modularization.

try:
	import psyco
	psyco.full()
except ImportError:
	pass

# standard Python modules
from types import *
import math
from copy import copy, deepcopy

# non-Graphite extensions
import pid as PID
from pid import *
import colors
import Num


# Graphite modules
from property import *
from primitive import *
from utility import *
from constants import *
# from axis import Axis, LinearAxis, LogAxis
from axis import *

#----------------------------------------------------------------------
# general vector- and matrix-handling functions...
# 		There might be easier ways to do these,
#		or these maybe should be moved elsewhere.
#		Or, perhaps they should be inlined for performance.

def dist(v):
	"return the length (distance) of vector v"
	return Num.sqrt(Num.sum(v*v))

def cross(v1,v2):
	"return the cross product of v1 and v2" \
	"  (NOTE: not appropriate for extended (4-element) vectors)"
	return Num.array(
			[	v1[1]*v2[2] - v1[2]*v2[1],
				v1[2]*v2[0] - v1[0]*v2[2],
				v1[0]*v2[1] - v1[1]*v2[0]	])

def scale4x4(sx, sy, sz):
	"return a 4x4 scaling matrix, scaling by sx, sy, and sz"
	return Num.array( [ \
			[sx, 0, 0, 0],
			[0, sy, 0, 0],
			[0, 0, sz, 0],
			[0, 0, 0, 1] ])

def translate4x4(tx, ty, tz):
	"return a 4x4 translation matrix, translating by tx, ty, and tz"
	return Num.array( [ \
			[1, 0, 0, tx],
			[0, 1, 0, ty],
			[0, 0, 1, tz],
			[0, 0, 0, 1] ])

dot = Num.dot

#
# Note: to apply one of the above transformations T to a point P = [x,y,z,1],
# just compute dot(T,p).
#
# To combine two transformations, applying T1 and then T2, compute dot(T2,T1).
#

def viewMatrix(eye, poi, perspective=0):
	"return a view transformation matrix given the eye loc and point of interest"
	# references:
	# 	http://www.cs.gsu.edu/classes/hypgraph/scanline/viewtran/view3d/3dview1.htm
	#	http://www2.cs.utah.edu/~cs6600/view/node11.html

	# first find new basis vectors u,v,n
	eye = Num.array(eye, Num.Float)			# make sure these are Float arrays
	poi = Num.array(poi,Num.Float)
	n = poi - eye
	n = n/dist(n)

	u = cross(n, (0,-1.0,0))
	u = u/dist(u)

	v = cross(n, u)
	v = v/dist(v)
			
	# then compute the transformation matrix
	# NOTE: I have inverted all the values in the 'z' column 
	#	so that the positive Z axis extends out of the screen,
	#	which is better for graphing applications.
	m = Num.array( \
			[	(u[0],	u[1],	-u[2],	-dot(eye,u)),
				(v[0],	v[1],	-v[2],	-dot(eye,v)),
				(n[0],	n[1],	-n[2],	-dot(eye,n)),
				(0,		0,		0,		1) ] )
	
	if perspective:
		# http://www2.cs.utah.edu/~cs6600/view/node17.html
		m[3][2] = -1/dist(poi-eye)
	
	
	return m

class AllClipped(Exception):
	def __init__(self):
		Exception.__init__(self)


# clipping functions
def clipLine(p0, p1, bounds):
	"""Clip the line from p0 to p1 by modifying the points;
	return None if the clipped line is empty.
	Else, return a (p0original, p1original) tuple saying if either
	point has been modified.
	"""
	f0 = [ 0.0 ]
	f1 = [ 0.0 ]
	delta = p1 - p0
	for axis in (X,Y,Z):
		if p0[axis] < bounds[axis][MIN]:
			# First point less than min
			if p1[axis] < bounds[axis][MIN]:
				# Both points less than min.
				raise AllClipped
			f0.append( (bounds[axis][MIN]-p0[axis]) / delta[axis] )

		elif p0[axis] > bounds[axis][MAX]:
			if p1[axis] > bounds[axis][MAX]:
				raise AllClipped
			f0.append( (bounds[axis][MAX]-p0[axis]) / delta[axis] )
		
		if p1[axis] < bounds[axis][MIN]:
			# point 1 less than min
			f1.append( (bounds[axis][MIN]-p1[axis]) / delta[axis] )

		elif p1[axis] > bounds[axis][MAX]:
			# point 1 greater than max
			f1.append( (bounds[axis][MAX]-p1[axis]) / delta[axis] )
	if len(f0)>1 or len(f1)>1:
		if len(f0) > 1:
			p0 = p0 + max(f0) * delta
		if len(f1) > 1:
			p1 = p1 + max(f0) * delta
	return (p0, p1, len(f0)>1, len(f1)>1)


def ptInBounds(pt, bounds):
	"return whether or not the given point lies within the 'bounds' 3D box."
	for axis in (X,Y,Z):
		if not bounds[axis][MIN] <=  pt[axis] <= bounds[axis][MAX]:
			return False
	return True
	
_NAtype = type(Num.array((1)))

#----------------------------------------------------------------------
class Dataset(object):
	"""Class: Dataset
	Purpose: provides data to the plot.  It's just a container to
	which data may be attached.  All the sequences (or functions) on
	a single Dataset object go together, e.g. the 'x' sequence aligns
	with the 'y' sequence to produce x,y data points.

	
	Notes: The trick here is to keep it easy to use in the easy cases,
	while also being flexible enough to handle the hard cases.	
	"""
	ATTR = ('x', 'y', 'z')
	
	def __init__(self, data=None):
		"""Normally called as Dataset( [ (x,y), (x,y), ... ] ), or as
		Dataset( [ (x,y,z), (x,y,z), ... ] ).
		Input may also be a Nx1, Nx2 or Nx3 Numeric python (or numarrray) array:
		Dataset( a ).   It may also be called without an argument to
		produce an empty container, which then must later be filled by calls
		to self.set*().
		"""
		if data is not None:
			elemsize = len(data[0])
			if elemsize == 1:
				self.y = Num.array(data)
			elif elemsize == 2:
				self.setXY(data)
			elif elemsize == 3:
				self.setXYZ(data)
			else:
				raise TypeError, "Data passed to Dataset constructor is of unknown dimensions."
	
	def _clear(self):
		for attr in self.ATTR:
			if hasattr(self, attr):
				delattr(self, attr)

	def set(self, attrlist, data):
		"""Set data from a list of n-tuples.
		Attrlist tells what each member of a tuple is.
		Usage: dataset.set(('x', 'y'), [(1, 0.3), (3, 0.1) ] )
		"""
		self._clear()
		tmp = Num.array(data)
		for (i, attr) in enumerate(attrlist):
			if attr in self.ATTR:
				setattr(self, attr, tmp[:,i])

	def setXY(self, xydata):
		"Shortcut method to set x and y data from a sequence of (x,y) pairs."
		self._clear()
		tmp = Num.array(xydata)
		self.x = tmp[:,0]
		self.y = tmp[:,1]
	
	def setXYZ(self, xydata):
		"Shortcut method to set x, y, and z data from a sequence of (x,y,z) triplets."
		self._clear()
		tmp = Num.array(xydata)
		self.x = tmp[:,0]
		self.y = tmp[:,1]
		self.z = tmp[:,2]
	
	def __len__(self):
		"Return the length of the dataset."
		l = []
		for attr in self.ATTR:
			if hasattr(self, attr):
				l.append(getattr(self, attr).shape[0])
		if len(l) == 0:
			return 0
		return min(l)

	def __getattr__(self, attr):
		"If the given attribute is not found but is one of our standard dimensions, " \
		"then add it with a sequence of default values."
		if attr in self.ATTR:
			qty = len(self)
			if attr == 'x':
				setattr(self, attr, Num.arange(qty))	# special case for x defaults
			else:
				setattr(self, attr, Num.zeros((qty,), Num.Int))
			return getattr(self,attr)
		raise AttributeError, attr
	
#----------------------------------------------------------------------
#----------------------------------------------------------------------
class PlotFormat(PropHolder):
	"""Class PlotFormat
	Purpose: defines a format (methods and parameters) used to draw
			 a data series.
	Notes: This abstract base class currently doesn't do anything,
		   but it's good design to have it anyway.
	"""
	
	_properties = {}

	def __init__(self):
		"Constructor -- initializes member variables."
		raise TypeError, "instantiating abstract class PlotFormat; " \
			"use a derived class instead"
	
	def submit(self,primitives,dataset, dataTrans=None, dataBounds=None):
		"add drawing elements for the given data set to the list of primitives"
		raise NotImplementedError, "derived class does not implement 'submit'"
		
	# in the future these functions might take blocked out values into account	
	def getXMin(self,dataset):
		"return the minimum x value of the given dataset"
		return min(dataset.x)

	def getXMax(self,dataset):
		return max(dataset.x)
		
	def getYMin(self,dataset):
		return min(dataset.y)
		
	def getYMax(self,dataset):
		return max(dataset.y)
		
	def getZMin(self,dataset):
		return min(dataset.z)
		
	def getZMax(self,dataset):
		return max(dataset.z)
		
class PointPlot(PlotFormat):
	"""Class PointPlot
	Purpose: defines a format (methods and parameters) used to draw
			 a line and/or scatter plot of a data series.
	"""
	
	_properties = {
			'lineStyle' : ClassProperty(LineStyle, LineStyle(),
					'style used to draw the lines, or None if no lines are desired'),
			# OFI: create a CallableProperty or ClassProperty to restrict this one:
			'symbol' : Property(None, # CircleSymbol,
					'class of symbol to be used, or None if no symbols are desired'),
			'symbolStyle' : ClassProperty(SymbolStyle, SymbolStyle(),
					'style used to draw the symbols') \
			}

	def __init__(self, lineStyle=UNSPECIFIED, symbol=UNSPECIFIED,
			symbolStyle=None):
		"Constructor -- initializes member variables."
		PropHolder.__init__(self)
		if symbol != UNSPECIFIED:
			self.symbol = symbol
		# NOTE: lineStyle and symbolStyle are objects; we must be careful
		# to copy them if used as defaults, otherwise, users would accidentally
		# change the defaults when they meant to change just one plot.
		# OFI: make sure we do this properly elsewhere, too!
		if lineStyle != UNSPECIFIED:
			self.lineStyle = lineStyle
		else:
			self.lineStyle = deepcopy(self.lineStyle)
		if symbolStyle and symbolStyle != UNSPECIFIED:
			self.symbolStyle = symbolStyle
		else:
			self.symbolStyle = deepcopy(self.symbolStyle)

	def __repr__(self):
		#return "PointPlot(lineStyle=%s, symbol=%s, symbolStyle=%s)" % \
		#	(self.lineStyle, self.symbol, self.symbolStyle)
		return "PointPlot()"

	def exportString(self,selfname): 
		"Returns a string with all field assignments."
		retval = self.exportStringFunc(selfname,
			proplist = ('lineStyle', 'symbol', 'symbolStyle'))
		return retval


	def submit(self, primitives, dataset, dataTrans=None, dataBounds=None):
		"""Add drawing elements for the given data set to the list of primitives."""
		
		if not dataTrans:
			dataTrans = lambda x:x

		# apply the data transformation to (a copy of) our data
		pts = [
			dataTrans( (x, y, z, 1) )
				for (x,y,z) in zip(dataset.x, dataset.y, dataset.z)
			]
		
		# apply it to the bounding box, too
		bounds = [None]*3
		bmin = dataTrans( (dataBounds[X][MIN], dataBounds[Y][MIN], dataBounds[Z][MIN], 1) )
		bmax = dataTrans( (dataBounds[X][MAX], dataBounds[Y][MAX], dataBounds[Z][MAX], 1) )
		for axis in (X,Y,Z):
			bounds[axis] = (bmin[axis], bmax[axis])
		
		if self.lineStyle:
			# We'll draw a line for each segment,
			# clipped to the given bounds.
			# But, in order to properly connect the segments
			# when using dashed lines and such,
			# we must separately keep track of the order in
			# which they were submitted.
			prevSegment = None
			for i in range(1, len(dataset)):
				try:
					cep0, cep1, p0clip, p1clip = clipLine(pts[i-1], pts[i], bounds)
				except AllClipped:
					# segment was clipped completely
					prevSegment = None
					# continue
				else:
					if p0clip:
						prevSegment = None

					if callable(self.lineStyle):
						lineStyle = self.lineStyle((i-1,i))
					else:
						lineStyle = self.lineStyle

					thisSegment = Line(cep0, cep1,
								style = lineStyle,
								prevSegment = prevSegment)
					primitives.append( thisSegment )

					if p1clip:
						prevSegment = None
					else:
						prevSegment = thisSegment

		if self.symbol and self.symbolStyle:
			for (i, pt) in enumerate(pts):
				if ptInBounds(pt, bounds):
					if callable(self.symbolStyle):
						symbolStyle = self.symbolStyle(i)
					else:
						symbolStyle = self.symbolStyle
					primitives.append( self.symbol(pt, style=symbolStyle) )




class BarPlot(PlotFormat):
	"""Class BarPlot
	Purpose: defines a format (methods and parameters) used to draw
			 a bar chart of a data series.  Actually, it just draws
			 one uniform set of bars; it will work in conjunction
			 with other BarPlots to produce a completed bar chart.

	Notes: there is currently no good way to specify that 'shift' and 'size' should
		   be auto-set by looking at all bars on the plot.  This needs to be fixed.
	"""
	
	_properties = {
			'lineStyle' : ClassProperty(LineStyle, LineStyle(),
					'style used to outline the bars, or None if no outlines are desired'),
			'fillStyle' : ClassProperty(Color, colors.black,
					'style (for now, just color) used to fill the bars'), 
			'axis' : EnumProperty(Y, "in which axis the bars extend", (X,Y,Z)),
			
			'base' : FloatProperty(0, "base value (in data coordinates) of the bars"),
			
			'shift' : ListProperty( FloatProperty(0,''), (0,0,0),
					'position shift applied to each bar (in data coordinates)', minqty=3, maxqty=3),
			'size' : ListProperty( FloatProperty(0.1,'',minval=0), (0.1,0.1,0.1),
					'x,y,z size of bars (in data coordinates)') \
			}

	def __init__(self, lineStyle=None, fillStyle=None):
		"Constructor -- initializes member variables."
		PropHolder.__init__(self)
		if lineStyle: self.lineStyle = lineStyle
		if fillStyle: self.fillStyle = fillStyle

	def __repr__(self):
		return "BarPlot()"
	
	def exportString(self,selfname): 
		"Returns a string with all field assignments."
		#retval = ""

		## for each of the axis properties print out a help comment and the value
		#for prop in ('lineStyle','fillStyle','axis','base','shift','size'):
		#	retval = retval + self.formatFunc(prop,selfname)
		return self.exportStringFunc(selfname,
			proplist = ('lineStyle','fillStyle','axis','base','shift','size'))

	def submit(self,primitives,dataset, dataTrans=None, dataBounds=None):
		"add drawing elements for the given data set to the list of primitives"
		
		if not dataTrans: dataTrans = lambda x:x

		# apply the data transformation to (a copy of) our data points,
		# and to another copy which has its base axis set to base value
		qty = len(dataset)
		toppts = [0]*qty		# top points (in a vertical bar)
		botpts = [0]*qty		# bottom points
		shift = self.shift + [0]
		for i in range(len(dataset)):
			point = [dataset.x[i], dataset.y[i], dataset.z[i], 1]
			toppts[i] = dataTrans( Num.add(point, shift) )
			point[self.axis] = self.base
			botpts[i] = dataTrans( Num.add(point, shift) )
		
		# apply it to the bounding box, too
		bounds = [None]*3
		bmin = dataTrans( (dataBounds[X][MIN],dataBounds[Y][MIN],dataBounds[Z][MIN],1) )
		bmax = dataTrans( (dataBounds[X][MAX],dataBounds[Y][MAX],dataBounds[Z][MAX],1) )
		for axis in (X,Y,Z):
			bounds[axis] = (bmin[axis],bmax[axis])
		
		# we'll draw a box primitive for each segment
		# LATER: clip to the given bounds
		# Find the corners of the box, by adding the size to one and subtracting
		# from the other.
		size = self.size + [0]		# but don't change the bounds
		size[self.axis] = 0			# in the dependent-measure axis!
		
		# transform size vector and origin to calculate size vector in view space
		size = dataTrans( size ) - dataTrans( [0,0,0,0] )
		size = size/2	# will add and subtract half the size from center to get full size
		
		for i in range(len(toppts)):
			if toppts[i][Y] < botpts[i][Y]:
				temp = toppts[i][Y]				
				toppts[i][Y] = botpts[i][Y]
				botpts[i][Y] = temp
			botpts[i] = botpts[i] + size
			toppts[i] = toppts[i] - size
				
			primitives.append( Box(botpts[i], toppts[i], 
					lineStyle=self.lineStyle, fillStyle=self.fillStyle) )


#----------------------------------------------------------------------
class Graph(PropHolder):
	"""Class: Graph
	Purpose: keeps all the information needed to plot a particular graph
	Notes: A Graph is basically a combination of a Frame (which defines
		   the axes) and some Primitives (things which can submit themselves
		   for rendering).
	"""
	
	# declare properties of this class
	_properties = {
		'datasets': ListProperty( ClassProperty(Dataset, None, ''), [], 
			"list of Dataset objects to be plotted by this graph"),
		'formats': ListProperty( ClassProperty(PlotFormat, None, ''), [PointPlot()], 
			"list of PlotFormat objects which will be used in a round-robin fashion by the Datasets"),
		'axisMappings': ListProperty( ListProperty( IntProperty(0,''), [], ''), [(0,1,2)],
			"list of mappings used by Datasets in round-robin fasion, \
			each mapping specifies which axes a Dataset should use for x,y, and z"),
		'overlays': ListProperty( ClassProperty(Primitive, None, ''), [],
			"list of 3D primitives using view coordinates which should be drawn with the graph"),
		
		'title': ClassProperty(Text, Text('',pos=(0.5,1.1,0),
			style=TextStyle(hjust=CENTER, vjust=BOTTOM, font=PID.Font(size=16))), 
			"Graph title, position given in frame coordinates"),

		'top': FloatProperty(30.0, "SPING y screen coordinate for top of graph frame", minval=0.0 ),
		'left': FloatProperty(80.0, "SPING x screen coordinate for left of graph frame", minval=0.0 ),
		'bottom': FloatProperty(250.0, "SPING y screen coordinate for bottom of graph frame", minval=0.0 ),
		'right': FloatProperty(390.0, "SPING x screen coordinate for right of graph frame", minval=0.0 ),
		
		'axes': ListProperty( ClassProperty(Axis,None,''),
					[LinearAxis('X'), LinearAxis('Y'), LinearAxis('Z')],
			"list of axes defined for the graph, axisMappings contains indexes into this list"),
		'lookAt': ListProperty( FloatProperty(0,''), [0.5,0.5,0.5],
			"point in view space at which the camera is looking", minqty=3, maxqty=3 ),
		'eyePosition': ListProperty( FloatProperty(0,''), [0.5,0.5,-5],
			"position of the camera (in view coordinates)", minqty=3, maxqty=3 ),
		'perspective': BoolProperty(0, "if true, use a perspective projection" )
	}

	DEFAULT_TITLE_POS = (0.5, 1.1, 0.0)
		
	def __init__(self):
		"Constructor -- initializes member variables."
		
		PropHolder.__init__(self)

		self.datasets = deepcopy(self.datasets)			# data sets (multi-dimensional sequences of numbers)
		self.formats = deepcopy(self.formats)			# graph format for each data set (Format objects)
		self.axisMappings = deepcopy(self.axisMappings)	# which axes to use for x,y,z for each dataset

		self.overlays = deepcopy(self.overlays)			# extra graph elements
		
		self.title = deepcopy(self.title)
		
		self.axes = deepcopy(self.axes)
		self.lookAt = deepcopy(self.lookAt)
		self.eyePosition = deepcopy(self.eyePosition)
		self.perspective = 0

	def exportString(self,selfname="g"):
		"Returns a string with all field assignments except for datasets."
		return self.exportStringFunc(selfname,
			proplist = ('formats','axisMappings','overlays', 'title','top',
				'left','bottom','right','axes','lookAt','eyePosition','perspective'),
			compProplist = ['formats','axes'])


	def draw(self, canvas):
		"Draw this graph into the given SPING canvas."
		# Steps:
		#	1. break the axes and all elements into a big list of drawing primitives
		#		in 3D data coordinates, handled by the submit call
		#	2. transform to 3D view coordinates and sort by Z (i.e., distance
		#		from the camera)
		#	3. transform again to screen coordinates, and draw each one
		
		primitives = []

		self.submit(primitives)
		
		# transform by the frame (world to view) transformation
		viewtrans = self.getViewTrans()
		# print viewtrans
		for item in primitives:
			item.transform4x4(viewtrans)
		# ... we'll skip the sorting for now...
		
		# finally, transform to screen coordinates and draw
		scaleX = self.right - self.left
		offsetX = self.left + scaleX/2
		scaleY = -(self.bottom - self.top)
		offsetY = self.bottom + scaleY/2
		# build a 4x4 matrix that implements both scaling and translation of X and Y
		transformation = Num.array(
					[ (scaleX,0,0,offsetX),
					  (0,scaleY,0,offsetY),
					  (0,0,1,0),
					  (0,0,0,1)	] );
		for item in primitives:
			item.transform4x4(transformation)
			item.projectTo2D()
			item.draw(canvas)


	def getDataBounds(self, datasetNumber):
		"return the bounding box in data coordinates for a given dataset, " \
		"in ([xmin,xmax],[ymin,ymax],[zmin,zmax]) form"

		axismap = self.axisMappings[ datasetNumber % len(self.axisMappings) ]
		axes = map(lambda i,a=self.axes: a[i], axismap)
		
		return (axes[X].actualRange(), axes[Y].actualRange(), axes[Z].actualRange())
		
	def getDataTrans(self, datasetNumber):
		"return a transformation function that maps " \
		"	data coordinates --> frame coordinates" \
		" for a given data set index."

		axismap = self.axisMappings[ datasetNumber % len(self.axisMappings) ]
		axes = map(lambda i,a=self.axes: a[i], axismap)
		if isinstance(axes[X], LinearAxis) and isinstance(axes[Y], LinearAxis) \
				and isinstance(axes[Z], LinearAxis):
			# all axes are linear (hooray!) so just apply
			# a linear data transformation, composed of:

			# 1. translate to null the data origin
			lineartrans = translate4x4(-axes[X].origin(), -axes[Y].origin(), -axes[Z].origin())

			# 2. scale to normalize the data range
			lineartrans = dot(scale4x4(axes[X].scale(), axes[Y].scale(), axes[Z].scale()),
					lineartrans)
			
			# 3. scale to normalize to the viewing scale (for partial axes)
			lineartrans = dot(scale4x4(axes[X].viewScale(X), axes[Y].viewScale(Y),
					axes[Z].viewScale(Z)),  lineartrans)

			# 4. translate to null the viewing origin
			lineartrans = dot(translate4x4(axes[X].viewOrigin(X), axes[Y].viewOrigin(Y),
					axes[Z].viewOrigin(Z)), lineartrans)
					
			#print "lineartrans:"
			#print lineartrans
			return lambda datapoint,trans=lineartrans: dot(trans,datapoint)

		# We have at least one log axis; so we need to do a log transformation,
		# followed by the linear one.
		# LATER: make sure this works with clipped axes!
		# (It probably won't; copy approach above.)
		xfunc = axes[X].transform
		yfunc = axes[Y].transform
		zfunc = axes[Z].transform
		lineartrans = Num.array( \
				[	(axes[X].logscale(),0,0, -axes[X].logorigin()*axes[X].logscale()),
					(0,axes[Y].logscale(),0, -axes[Y].logorigin()*axes[Y].logscale()),
					(0,0,axes[Z].logscale(), -axes[Z].logorigin()*axes[Z].logscale()),
					(0,0,0,1)	] )
		return lambda d,trans=lineartrans, xfunc=xfunc, yfunc=yfunc, zfunc=zfunc: \
			dot(trans,[xfunc(d[X]), yfunc(d[Y]), zfunc(d[Z]), d[3]])		

	
	def getViewTrans(self):
		"""return a transformation matrix that does maps
			frame coordinates --> view coordinates"""

		return viewMatrix( self.eyePosition, self.lookAt, self.perspective )
		

	def submit(self, primitives):
		"append any drawing primitives for the axes onto the given list"
		# let's first draw the frame...
		# OFI: make this optional, or provide more control
		primitives.append( Line([0,0,0], [0,0,1]) )
		primitives.append( Line([0,0,0], [0,1,0]) )
		primitives.append( Line([0,0,0], [1,0,0]) )
		primitives.append( Line([0,0,1], [0,1,1]) )
		primitives.append( Line([0,0,1], [1,0,1]) )
		primitives.append( Line([0,1,0], [1,1,0]) )
		primitives.append( Line([0,1,0], [0,1,1]) )
		primitives.append( Line([1,0,0], [1,0,1]) )
		primitives.append( Line([1,0,0], [1,1,0]) )
		primitives.append( Line([1,1,1], [1,1,0]) )
		primitives.append( Line([1,1,1], [1,0,1]) )
		primitives.append( Line([1,1,1], [0,1,1]) )	
		
		# determine the range of data mapped to each axis
		# axisBounds = [(min,max),(min,max),...], one entry for each axis
		axisBounds = []
		# create an empty list of lists, as long as the number of axes
		datamin = [ [] for i in self.axes ]
		# (do the same for datamax)
		datamax = [ [] for i in self.axes ]
		lsf = len(self.formats)
		lsn = len(self.axisMappings)
		for i in range(len(self.datasets)):
			# determine which axes this dataset maps to
			Xaxis = self.axisMappings[i%lsn][0]
			Yaxis = self.axisMappings[i%lsn][1]
			Zaxis = self.axisMappings[i%lsn][2]
			# append the max and min to the various axes lists
			datamin[Xaxis].append( self.formats[i%lsf].getXMin(self.datasets[i]) )
			datamax[Xaxis].append( self.formats[i%lsf].getXMax(self.datasets[i]) )
			datamin[Yaxis].append( self.formats[i%lsf].getYMin(self.datasets[i]) )
			datamax[Yaxis].append( self.formats[i%lsf].getYMax(self.datasets[i]) )
			datamin[Zaxis].append( self.formats[i%lsf].getZMin(self.datasets[i]) )
			datamax[Zaxis].append( self.formats[i%lsf].getZMax(self.datasets[i]) )
		# assign each axis their data bounds, if no data was mapped
		# to this axis then set databounds to (0,1)
		for i in range(len(self.axes)):
			if datamin[i] == []:
				axisBounds.append( (0,1) )
			else:				
				axisBounds.append( (min(datamin[i]),max(datamax[i])) )
			
		#print "axisBounds = ", axisBounds
		for i in range(len(self.axes)):
			self.axes[i].setActualRange(axisBounds[i])
		
		# have the specified plot format for each dataset submit
		for i in range(len(self.datasets)):
			dataTrans = self.getDataTrans(i)
			bounds = self.getDataBounds(i) 
			format = self.formats[i%lsf] # round-robin use of formats
			format.submit(primitives, self.datasets[i], dataTrans, bounds)
		
		# then the axes
		for axis in self.axes:
			axis.submit(primitives)
		# add (a copy of) overlays to the list of primitives
		# (Why a copy?  Because they're going to get transformed, and we don't
		#  want to screw up the originals.)
		# OFI: currently overlays can only be done in frame coordinates, data would be good too
		primitives.extend( map(deepcopy, self.overlays) )
		
		# submit title, copy because want to keep original position
		title = deepcopy(self.title)
		if title.pos() is None:
			title.pos(self.DEFAULT_TITLE_POS)
		primitives.append(title)
	
