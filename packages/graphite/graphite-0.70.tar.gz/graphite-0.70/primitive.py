"""
Module Primitive
This module contains the Primitive class and its subclasses, used internally
by the Graphite plotting package.  It also contains the Style classes that
control their appearance (e.g., LineStyle and TextStyle).

Design: Each primitive takes its style object as a parameter for the
constructor.  Most primitives also accept information such as start
and end points as part of its constructor.  Symbols and FormattedLines
don't accept their positions until drawing time so that only one
instance is required for many draw calls.

Primitives
-points in 3D space
-ultimately transformed to SPING space

To Do:
	+ incorporate symbol.py into this file
	- make the Text primitive into formatted-text
	- fancier drawing, e.g. dashed or dot-dashed lines
"""

try:
	import psyco
	from psyco.classes import *
except ImportError:
	pass

import Num
import math

from property import *
import pid as PID
from pid import *
import colors
from colors import Color
import constants as C
from constants import X, Y, Z
import types


#----------------------------------------------------------------------

class LineStyle(PropHolder):
	"""Class: LineStyle
	Purpose: encapsulates settings used to draw a line
	"""

	# declare properties of this class
	_properties = {
		'width': FloatProperty(1, "width of the line, in points",
					minval=0.0,maxval=10),
		'period': FloatProperty(0.03, "period of the dashes, as a fraction of the canvas width",
					minval=0.001,maxval=1.0),
		'onfrac': FloatProperty(0.5, "length of the dashes, as a fraction of the period",
					minval=0.0, maxval=1.0),
		'color': ClassProperty(Color, colors.black, "SPING color of the line"),
		'kind': EnumProperty(C.SOLID, "kind of line",
					(C.SOLID, C.DASHED))
	}
	
	def __init__(self, width=1, color=colors.black, kind=C.SOLID):
		PropHolder.__init__(self)
		self.width = width
		self.color = color
		self.kind = kind

	def __repr__(self):
		return "LineStyle(width=%s, \n\tcolor=%s, kind=%s)" % \
			(self.width, self.color, self.kind)

#----------------------------------------------------------------------
class SymbolStyle(PropHolder):
	"""Class: SymbolStyle
	Purpose: encapsulates settings used to draw a symbol
	"""

	# declare properties of this class
	_properties = {
		'size': FloatProperty(1, "height and width of symbol, in points",
					minval=0.0,
					maxval=20),
		'fillColor': ClassProperty(Color, colors.black,
						"SPING color for the symbol fill"),
		'edgeWidth': FloatProperty(1, "width of outline, in points",
						minval=0,
						maxval=10),
		'edgeColor': ClassProperty(Color, colors.black,
						"SPING color for the outline")
	}
	
	def __init__(self, size=5, fillColor=colors.black, edgeWidth=1, edgeColor=colors.black):
		PropHolder.__init__(self)
		self.size = size
		self.fillColor = fillColor
		self.edgeWidth = edgeWidth
		self.edgeColor = edgeColor

	def __repr__(self):
		return "SymbolStyle(size=%s, \n\tfillColor=%s, \n\tedgeWidth=%s, \n\tedgeColor=%s)" % \
			(self.size, self.fillColor, self.edgeWidth, self.edgeColor)


#----------------------------------------------------------------------

class TextStyle(PropHolder):
	"""Class: TextStyle
	Purpose: encapsulates settings used to draw text
	"""

	# declare properties of this class
	_properties = {
		'hjust': EnumProperty(C.CENTER, "horizontal justfication: LEFT, CENTER, or RIGHT",
				(C.LEFT, C.CENTER, C.RIGHT)),
		'vjust': EnumProperty(C.CENTER, "vertical justification: TOP, CENTER, or BOTTOM",
				(C.TOP, C.CENTER, C.BOTTOM)),
		'font': ClassProperty(PID.Font, PID.Font(), "SPING base font (and font attributes)"),
		'color': ClassProperty(Color, colors.black, "SPING color of the text") \
	}
	
	def __init__(self, hjust=C.CENTER, vjust=C.CENTER, font=None, color=colors.black):
		PropHolder.__init__(self)
		self.hjust, self.vjust = hjust, vjust
		if font:
			self.font = font
		else:
			self.font = PID.Font()
		self.color = color

	def __repr__(self):
		return "TextStyle(hjust=%s, vjust=%s, \n\tfont=%s, \n\tcolor=%s)" % \
			(self.hjust, self.vjust, self.font, self.color)
	
#----------------------------------------------------------------------
#----------------------------------------------------------------------
class Primitive(object):
	"""Class: Primitive
	Purpose: abstracts any elemental drawing object in 3D space.  It
			 can be transformed, and can plot itself into a SPING
			 canvas (ignoring Z coordinate when doing so).
	"""

	def __init__(self):
		self.points = []
		
	def projectTo2D(self):
		"do the final transformation from extended 3D coordinates to 2D coordinates"
		for i in range(len(self.points)):
			self.points[i] = self.points[i] / self.points[i][3]
	
	def transform3x3(self, matrix):
		"Transform our control points by the given 3x3 transformation matrix."
		for i in range(len(self.points)):
			self.points[i] = Num.dot(matrix, self.points[i])

	def transform4x4(self, matrix):
		"transform our control points by the given 4x4 transformation matrix"
		for i in range(len(self.points)):
			# make an extended vector so we can do matrix mulitplication
			p = self.points[i]
			if len(p) < 4:
				p = Num.array( [p[0], p[1], p[2], 1] )
			self.points[i] = Num.dot(matrix, p)

	def draw(self, canvas):
		"draw self into the given SPING canvas (ignoring Z)"
		raise NotImplementedError, "draw"




class Line(Primitive):
	"""Class: Line
	Purpose: a 3D line primitive.
	"""
	
	def __init__(self, p1, p2, style=None, prevSegment=None):
		"""Constructor: creates a line from p1 to p2 (each of which is an (x,y,z) tuple).
		If prevSegment is non-null, this is a continuation of another line.
		"""
		assert len(p1)>=3
		assert len(p2)>=3
		self.points = [p1, p2]

		if style is not None:
			self.style = style
		else:
			self.style = LineStyle()

		self.state = None	# Whatever state info the drawing routine might need.
		self.prevSegment = prevSegment
	

	def draw(self, canvas):
		"Draw self into the given SPING canvas (ignoring Z)."
		if self.style.width < 0.01:
			return

		if self.style.kind == C.SOLID:
			self._drawSolid(canvas)
		else:
			self._drawDashed(canvas)


	def _drawSolid(self, canvas):
		canvas.drawLine(self.points[0][X], self.points[0][Y],
				self.points[1][X], self.points[1][Y],
				width=self.style.width, color=self.style.color )
	
	def get_state(self):
		"""Distance along the curve, from the beginning."""
		if self.prevSegment is None:
			self.state = 0.0
		else:
			self.state = self.prevSegment.state
		assert self.state >= 0.0
		return self.state

	def incr_state(self, dist):
		self.state += dist
		return self.state
		

	def _drawDashed(self, canvas):
		"""Draw self into the given canvas, as a dashed line."""

		if self.style.onfrac < 0.001:
			return

		x1 =	float(self.points[0][X])
		y1 =	float(self.points[0][Y])
		x2 =	float(self.points[1][X])
		y2 =	float(self.points[1][Y])

		x = x1
		y = y1

		period = float(self.style.period) * 256.0
		position = self.get_state() % period
		onfrac = float(self.style.onfrac)
		peron = period * onfrac
		# find our x- and y-increments per period:
		dist = math.hypot(x2-x1, y2-y1)
		if dist <= 0:
			return
		xcos = float(x2-x1)/dist
		ycos = float(y2-y1)/dist
		# dxon = dx * onfrac
		# dyon = dy * onfrac

		w = self.style.width
		c = self.style.color

		while dist > 0:
			# First, we advance to the end of the current period, if possible
			if position < peron and dist+position < peron:
				# The entire line segment is within the 'on' part of the dash.
				# Draw it, increment state, and return.
				canvas.drawLine(x, y, x2, y2, width=w, color=c)
				self.state += dist
				return
			elif position < peron:
				# The line segment starts within the 'on' part of a dash,
				# but extends beyond.
				# Draw to end of 'on' part.
				step = peron - position
				xe = x+xcos*step
				ye = y+ycos*step
				canvas.drawLine(x, y, xe, ye, width=w, color=c)
				x = xe
				y = ye
				position += step
				dist -= step
			# If we get here, we are within the 'off' part of the dash.
			if dist+position < period:
				# The segment ends in the 'off part of the dash.
				# Increment the state to the end and return.
				self.state += dist
				return
			else:
				# If we get here, the segment has crossed into the next
				# period.
				step = period - position
				dist -= step
				self.state += step
				position = 0.0
				x = x+xcos*step
				y = y+ycos*step




class Box(Primitive):
	"""Class: Box
	Purpose: a 3D box primitive.
	"""
	
	def __init__(self, p1, p2, lineStyle=None, fillStyle=None):
		"Constructor: creates a box from p1 to p2 (each of which is an (x,y,z) tuple)"

		assert len(p1) >= 3
		assert len(p2) >= 3
		# Now p1, p2 are 3D points diagonally opposite on the box.
		# Note that while it takes only 2 points to define a box in 3D space,
		# we must keep all 8 corners around or we will lose important info
		# when the box is projected into 2D space.		
		self.points = [p1,				# bottom left back
				[p1[X],p2[Y],p1[Z]],	# top left back
				[p2[X],p2[Y],p1[Z]],	# top right back
				[p2[X],p1[Y],p1[Z]],	# bottom right back
				[p1[X],p1[Y],p2[Z]],	# bottom left front
				[p1[X],p2[Y],p2[Z]],	# top left front
				p2,						# top right front
				[p2[X],p1[Y],p2[Z]]]	# bottom right front
		
		if lineStyle is not None: self.lineStyle = lineStyle
		else: self.lineStyle = LineStyle()
		if fillStyle is not None: self.fillStyle = fillStyle
		else: self.fillStyle = colors.black
		
	def draw(self, canvas):
		"draw self into the given SPING canvas (ignoring Z)"
		# NOTE: we shouldn't be doing this final transformation here;
		# rather, it should be implemented at a higher level somewhere
		corners = [0]*8
		for i in range(8):
			corners[i] = (self.points[i][X], self.points[i][Y])
		# draw all 3 sides which face the camera
		if corners[BLF][X] < corners[BRF][X]:
			# ...front
			canvas.drawPolygon( [corners[BLF], corners[TLF],
						corners[TRF], corners[BRF]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )
		else:
			# ... back
			canvas.drawPolygon( [corners[BLB], corners[TLB],
						corners[TRB],corners[BRB]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )

		if corners[BRF][X] < corners[BRB][X]:
			# ...right
			canvas.drawPolygon( [corners[BRB], corners[TRB],
						corners[TRF],corners[BRF]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )
		else:
			# ...left
			canvas.drawPolygon( [corners[BLB], corners[TLB],
						corners[TLF],corners[BLF]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )

		if corners[TLF][Y] > corners[TLB][Y]:
			# ...top
			canvas.drawPolygon( [corners[TLB], corners[TLF],
						corners[TRF],corners[TRB]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )
		else:
			# ...bottom
			canvas.drawPolygon( [corners[BLB], corners[BLF],
						corners[BRF],corners[BRB]],
						edgeWidth=self.lineStyle.width,
						edgeColor=self.lineStyle.color,
						fillColor=self.fillStyle, closed=1 )
		

# constants used to identify box corners above... just for convenience
BRF,TRF,TLF,BLF,BRB,TRB,TLB,BLB,  = range(8)	

#----------------------------------------------------------------------
class Symbol(Primitive):
	"""Class: Symbol
	Purpose: This is the base class for a symbol.  Each type of symbol
	  will be its own subclass.
	"""
	registry = []

	
	def __init__(self, pos, style=None):
		"Constructor: initializes the symbol's style."
		self.points = [pos]
		if style is not None: self.style = style
		else: self.style = SymbolStyle()

	def draw(self,canvas):
		"Draws the symbol on canvas."
		raise NotImplementedError, 'draw'

	def _register(cls, name, theClass):
		cls.registry.append( (name, theClass) )
	_register = classmethod(_register)

	def G(cls, name):
		if type(name) == types.IntType:
			return cls.registry[name][1]
		for (n, cl) in cls.registry:
			if n == name:
				return cl
		return cls.registry[abs(hash(name))%len(cls.registry)][1]
	G = classmethod(G)


class CircleSymbol(Symbol):
	"""Class: CircleSymbol
	Purpose: implements the circle symbol
	"""
	
	def draw(self,canvas):
		x = self.points[0][X]
		y = self.points[0][Y]
		canvas.drawEllipse( x - (self.style.size/2),
				y - (self.style.size/2),
				x + (self.style.size/2),
				y + (self.style.size/2),
				fillColor=self.style.fillColor,
				edgeWidth=self.style.edgeWidth,
				edgeColor=self.style.edgeColor
				)

Symbol._register('circle', CircleSymbol)

class _polySymbol(Symbol):
	def corners(self):
		raise RuntimeError, "Virtual Function"

	def draw(self,canvas):
		x,y = (self.points[0][0], self.points[0][1])
		sss = self.style.size/2.0
		corners = [
			(x+sss*dx, y+sss*dy) for (dx, dy) in self.corners()
			]
		canvas.drawPolygon( corners,
				fillColor=self.style.fillColor,
				edgeWidth=self.style.edgeWidth,
				edgeColor=self.style.edgeColor,
				closed=1)
			  
class SquareSymbol(_polySymbol):
	"""Class: SquareSymbol
	Purpose: implements the square symbol
	"""

	_c = [ (-1, -1), (-1, 1), (1, 1), (1, -1) ]
	def corners(self):
		return self._c
Symbol._register('square', SquareSymbol)

class UTriangleSymbol(_polySymbol):
	""" Purpose: draws an upside-down triangle.
	"""
	
	r3 = math.sqrt(3.0)
	_c = [ (0, r3), (-1, -(2-r3)),
				(1, -(2-r3))
			]

	def corners(self):
		return self._c

Symbol._register('utriangle', UTriangleSymbol)

class TriangleSymbol(_polySymbol):
	""" Purpose: draws a triangle.
	"""
	
	r3 = math.sqrt(3.0)
	_c = [ (0, -r3), (-1, (2-r3)),
				(1, (2-r3))
			]

	def corners(self):
		return self._c

Symbol._register('triangle', TriangleSymbol)

class VstrokeSymbol(_polySymbol):
	"""Purpose: implements a vertical stroke with
	a little bump in the middle.
	"""
	
	_c = [ (0.4, 0), (0.125, 0.5), (0.125, 1),
				(-0.125, 1), (-0.125, 0.5),
				(-0.4, 0), (-0.125, -0.5),
				(-0.125, -1), (0.125, -1),
				(0.125, -0.5), (0.4, 0)
			]

	def corners(self):
		return self._c

Symbol._register('vstroke', VstrokeSymbol)

class HstrokeSymbol(_polySymbol):
	"""Purpose: implements a horizontal stroke with
	a little bump in the middle.
	"""
	_c = [ (0.4, 0), (0.125, 0.5), (0.125, 1),
				(-0.125, 1), (-0.125, 0.5),
				(-0.4, 0), (-0.125, -0.5),
				(-0.125, -1), (0.125, -1),
				(0.125, -0.5), (0.4, 0)
			]
	_c = [ (y, x) for (x, y) in _c ]

	def corners(self):
		return self._c
	
Symbol._register('hstroke', HstrokeSymbol)




#----------------------------------------------------------------------
class Text(Primitive):
	"""Class: Text
	Purpose: a string to be drawn at some position in 3D space.
	If you do not specify the pos, it might either have a sensible
	default applied later (like the title), or it might just raise
	an exception.
	"""
	
	def __init__(self, text='?', pos=None, style=None, angle=0):
		"Constructor: creates a text object at the given location"
		self.text = str(text)
		self.points = [pos]
		self.angle = angle
		if style is not None:
			self.style = style
		else:
			self.style = TextStyle()		

	def pos(self, p=None):
		op = self.points[0]
		if p is not None:
			self.points = [p]
		return op

	def __repr__(self):
		return "Text('%s', pos=%s, \n\tstyle=%s, \n\tangle=%s)" % \
			(self.text, self.points[0], self.style, self.angle)
	
	def draw(self, canvas):
		"draw self into the given SPING canvas (ignoring Z)"
		assert self.points[0] is not None, "No position was set for text=(%s...) " % self.text[:6]
		x = self.points[0][X]
		y = self.points[0][Y]
		
		# use stringformat.py to give us cool formatting of style,
		# greek letters, super/subscript, etc.
		ascent = stringformat.fontAscent(canvas, self.style.font)
		width = stringformat.stringWidth(canvas, self.text, font=self.style.font)

		radians = self.angle * math.pi/180.0
		if self.style.vjust == C.TOP:
			x += math.sin(radians) * ascent
			y += math.cos(radians) * ascent
		elif self.style.vjust == C.CENTER:
			x += math.sin(radians) * ascent/2
			y += math.cos(radians) * ascent/2

		if self.style.hjust == C.CENTER:
			wfrac = 0.5
		elif self.style.hjust == C.RIGHT:
			wfrac = 1.0
		elif isinstance(self.style.hjust, C.AlignChar):
			wfrac = self.style.hjust.align(self.text)
		else:
			wfrac = 0.0
		x -= math.cos(radians) * width * wfrac
		y += math.sin(radians) * width * wfrac

		stringformat.drawString( canvas, self.text, x, y,
				font=self.style.font, color=self.style.color, angle=self.angle )


############################################################## testing ####
#def symtest():
#	import piddleQD
#	canvas  = piddleQD.QDCanvas( size=(400,300) )
#
#	# the circle symbol
#	sym = CircleSymbol( (100,100,0) )
#	sym.draw(canvas)
#
#	sym = CircleSymbol( (200,100,0), SymbolStyle())
#	sym.draw(canvas)
#
#	sym = CircleSymbol( (20,40,0), SymbolStyle(size=5,fillColor=red))
#	sym.draw(canvas)
#	
#	# the square symbol
#	sym = SquareSymbol( (15,30,0), SymbolStyle(size=8,edgeColor=yellow,edgeWidth=2))
#	sym.draw(canvas)
#	
#def dashtest():
#	import piddleQD
#	global canvas
#	try: canvas.close()
#	except: pass
#	canvas = piddleQD.QDCanvas()
#	line = Line( (10,10,0,1), (94,50,0,1), LineStyle(width=1, kind=C.DASHED) )
#	line.draw(canvas)
#
#	line = Line( (10,20,0,1), (94,60,0,1), LineStyle(width=1, kind=C.SOLID) )
#	line.draw(canvas)
#	
##symtest()
#dashtest()
