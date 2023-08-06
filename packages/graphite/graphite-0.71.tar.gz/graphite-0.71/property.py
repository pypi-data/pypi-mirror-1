"""property.py
This module defines classes dealing with properties, which are object
attributes that have descriptions restricted values.

April 1999 JJS

Revisions:

 5/08/99 JJS: added dir() and help() module-level functions;
			  added ClassProperty and ListProperty.

"""

import types

import sys
if hasattr(sys, 'maxint'):
	MAXINT = sys.maxint
else:
	MAXINT = 0x7FFFFFFF		# +2147483647
MININT = (-MAXINT)-1
MAXFLOAT = 1e+308
MINFLOAT = -1e308

#----------------------------------------------------------------------
# replace standard dir() with a property-savvy version

def dir(arg=None):
	"""Modifies the standard dir() function to return a list of properties
	of a PropHolder object."""

	if arg is not None and isinstance(arg, PropHolder):
		return arg._properties.keys()
	olddir = __builtins__.dir
	if arg is None:
		return olddir()
	return olddir(arg)


def help(arg,arg2=None):
	if isinstance(arg, PropHolder):
		return arg.help(arg2)
	return arg.__doc__
	
#----------------------------------------------------------------------
def mkbool(val):
	"function to convert various things to 'bool' (0 or 1) values"
	try:
		temp = int(val)
		return temp != 0
	except:
		pass

	if type(val)==types.StringType and len(val)>0:
		c = val[0]
		return c not in ['N','n','F','f','0']

	return bool(val)
	

#----------------------------------------------------------------------
class DeferredProperty(object):
	"""Something that promises to produce the right kind of property, later."""
	def __init__(self, generator, type, *data):
		self.type = type
		self.generator = generator
		self.data = data

	def __call__(self, index):
		val = self.generator(index, *self.data)
		return val



class Property(object):
	"Base class of any property type.  Accepts any value."
	def __init__(self, defval, helpstr):
		self.defval = defval
		self.helpstr = helpstr

	def acceptable(self, val):
		"""Return two values: first is True/False unacceptable/acceptable,
		second is the value modified as needed to fit the type
		or an error string explaining the problem.
		"""
		return True, val

	def typestr(self):
		"return a short string indicating the type of this property"
		return "any"

	def ok_deferred(self, val, oktype):
		return isinstance(val, DeferredProperty) and val.type==oktype


class IntProperty(Property):
	"a property that accepts only integers"
	def __init__(self, defval, helpstr, maxval=MAXINT, minval=MININT):
		self.defval = int(defval)
		self.helpstr = helpstr
		self.minval, self.maxval = minval, maxval


	def acceptable(self, val):
		if self.ok_deferred(val, types.IntType):
			return True, val

		try:
			out = int(val)
		except:
			return False, "unable to convert to int: %s" % str(val)

		if out < self.minval or out > self.maxval:
			return False, "value %d out of range (%d to %d)" % \
				(out, self.minval, self.maxval)
		return True, out


	def typestr(self):
		"return a short string indicating the type of this property"
		return "int"


class FloatProperty(Property):
	"a property that accepts floating-point numbers"
	def __init__(self, defval, helpstr, maxval=MAXFLOAT, minval=MINFLOAT):
		self.defval = float(defval)
		self.helpstr = helpstr
		self.minval, self.maxval = minval, maxval
		

	def acceptable(self, val):
		if self.ok_deferred(val, types.FloatType):
			return True, val

		try:
			out = float(val)
		except:
			return False, "unable to convert to float: %s" % str(val)

		if out < self.minval or out > self.maxval:
			return False, "value %g out of range (%g to %g)" % \
				(out, self.minval, self.maxval)

		return True, out


	def typestr(self):
		"return a short string indicating the type of this property"
		return "float"



class BoolProperty(Property):
	"a property that stores boolean values"
	def __init__(self, defval, helpstr):
		self.defval = mkbool(defval)
		self.helpstr = helpstr
	
	def acceptable(self, val):
		if self.ok_deferred(val, types.BooleanType):
			return True, val
		return True, mkbool(val)

	def typestr(self):
		"return a short string indicating the type of this property"
		return "bool"



class EnumProperty(Property):
	"a property that accepts any of a finite set of constants"
	def __init__(self, defval, helpstr, vallist):
		self.helpstr = helpstr
		self.vallist = vallist
		ok, reason = self.acceptable(defval)
		if not ok:
			raise TypeError, reason
		self.defval = reason
		
	def acceptable(self, val):
		if self.ok_deferred(val, self.vallist):
			return True, val
		if val in self.vallist:
			return True, val
		return False, "%s not in acceptable values %s" % (val, self.vallist)

	def typestr(self):
		"return a short string indicating the type of this property"
		return "enum"


class ClassProperty(Property):
	"""a property that accepts only members of a class
	(or derived classes), or None."""

	def __init__(self, okclass, defval, helpstr):
		self.okclass = okclass
		self.helpstr = helpstr
		ok, reason = self.acceptable(defval)
		if not ok:
			raise TypeError, reason
		self.defval = reason
		
	def acceptable(self, val):
		if val is None:
			return True, val
		if self.ok_deferred(val, self.okclass):
			return True, val

		if isinstance(val, self.okclass):
			return True, val
		try:
			out = self.okclass(val)
			return True, out
		except:
			return False, "unable to convert to %s: %s" % (self.okclass.__name__, val)
	
	def typestr(self):
		"return a short string indicating the type of this property"
		return self.okclass.__name__


class ListProperty(Property):
	"""a property that accepts a list composed of elements
	of a given property type"""

	def __init__(self, elemtype, defval, helpstr, minqty=0, maxqty=32767):
		if not isinstance(elemtype, Property):
			raise TypeError, "list type must be a Property"
		self.elemtype = elemtype
		self.helpstr = helpstr
		self.minqty = minqty
		self.maxqty = maxqty
		ok, reason = self.acceptable(defval)
		if not ok:
			raise TypeError, reason
		self.defval = reason
		
	def acceptable(self,val):
		if self.ok_deferred(val, types.ListType):
			return True, val
		if type(val) != types.ListType:
			if type(val) == types.TupleType:
				val = list(val)
			else:
				val = [val]
		else:
			val = list(val)		# do a copy to avoid munging the original
		if len(val) < self.minqty:
			return 0, "list too short -- must contain at least %d elements" % self.minqty
		if len(val) > self.maxqty:
			return 0, "list too long -- must be at most %d elements" % self.maxqty
		
		for i in range(len(val)):
			elem = val[i]
			ok, result = self.elemtype.acceptable(elem)
			if not ok:
				return 0, result
			val[i] = result
		return True, val
	
	def typestr(self):
		"return a short string indicating the type of this property"
		if self.minqty > 0:
			if self.maxqty == self.minqty:
				return "list of %d %s" % (self.minqty, self.elemtype.typestr())
			if self.maxqty < 32767:
				return "list of %d to %d %s" % (self.minqty, self.maxqty, self.elemtype.typestr())
			return "list of at least %d %s" % (self.minqty, self.elemtype.typestr())
		if self.maxqty < 32767:
			return "list of at most %d %s" % (self.maxqty, self.elemtype.typestr())
		return "list of " + self.elemtype.typestr()



#----------------------------------------------------------------------
class PropHolder(Property):
	"""Base class of any object which can have properties."""
	_properties = None	# The derived class must define this
				# to be a dictionary mapping names to Properties

	def __init__(self, helpstr=''):
		self.__dict__['_protected'] = True
		# means you can't add any new attributes

		if not helpstr: helpstr = self.__doc__
		self.__dict__['helpstr'] = helpstr


	def __getattr__(self, attr):
		# This is called only when the requested
		# attribute has not yet been set.
		try:
			return self._properties[attr].defval
		except:
			raise AttributeError, attr


	def __setattr__(self, attr, val):
		# allow names which start with an underscore
		# to bypass property protection
		if attr.startswith('_'):
			self.__dict__[attr] = val
			return
			
		# first, see whether this is an existing property
		try:
			prop = self._properties[attr]
		except:
			# if not, see whether it's OK to add new properties
			if self.__dict__['_protected']:
				raise TypeError, "object is protected (can't add new attributes)"
		# now we know it's OK to assign to this property;
		# see whether the given value is acceptable
		ok, val = prop.acceptable(val)
		if not ok:
			raise ValueError, val
		self.__dict__[attr] = val


	def help(self,attr=None):
		if not attr:
			out = self.helpstr + '\nProperties:\n\n'
			for attr in self._properties.keys():
				prop = self._properties[attr]
				out = out + "   %s (%s): %s\n" %   \
					(attr, prop.typestr(), prop.helpstr)
			return out
		try:
			prop = self._properties[attr]
			return "%s (%s): %s" % (attr, prop.typestr(), prop.helpstr)


		except:
			return "%s is not a property" % attr
	
	def formatFunc(self,prop,sn,value):
		"generates a string with the given property's help string as a comment and value"
		# add a comment specifying whether this is default value
		comment = ""
		if getattr(self,prop) == self._properties[prop].defval:
			comment = "\t# default value"	
		return "# %s\n%s.%s = %s%s\n\n" % \
			(self._properties[prop].helpstr,sn,prop,value,comment)

	def exportStringFunc(self,selfname,proplist=[],compProplist=[]):
		"Utility function which returns a string with all values for given properties,"
		"and recursivesly calls exportString on complicated properties."
		retval = ""

		# for each of the properties in the given list print out a help comment and the value
		for prop in proplist:
			retval = retval + self.formatFunc(prop,selfname,getattr(self,prop))

			# check for more complicated properties
			if prop in compProplist:
				proplist = getattr(self,prop)
				for index in range(0,len(proplist)):    # for each instance in the list
					retval = retval + \
						proplist[index].exportString('%s.%s[%s]' % (selfname, prop, index) )

		return retval

	def default(self,attr):
		try:
			prop = self._properties[attr]
			return prop.defval
		except:
			return "%s is not a property" % attr

		
#----------------------------------------------------------------------
# testing...

BAR='BAR'
LINE='LINE'
SCATTER='SCATTER'

class TestClass(PropHolder):
	"just a test class for exercising properties"
	
	# declare properties of this class
	_properties = {
		'ref': Property('', "put anything you want here"),
		'fingers': IntProperty(10, "how many fingers you have",minval=0),
		'height': FloatProperty(1.7, "your height in meters",minval=0.5,maxval=3),
		'alive': BoolProperty(True, "whether or not you're breathing"),
		'type': EnumProperty(BAR, "type of plot", (BAR,LINE,SCATTER) ),
		'freckles': ListProperty( IntProperty(0,'',minval=0), (0,0,0,0),
						"freckles per limb", minqty=4, maxqty=4)
		 }	
	
	def __init__(self):
		PropHolder.__init__(self)

# t = TestClass()
# print dir(t)
# print dir(3)
# print dir()
