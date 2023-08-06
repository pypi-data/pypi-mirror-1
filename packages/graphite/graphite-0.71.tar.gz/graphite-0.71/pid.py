"""This is a compatibility module so that graphite
can use either sping (http://sping.sourceforge.net)
or piddle (http://piddle.sourceforge.net).
"""


try:
	import sping
	_s = True
except ImportError:
	_s = False

if not _s:
	try:
		import piddle
	except ImportError:
		raise ImportError, "Cannot import either sping or piddle."


if _s:
	from sping import *
	try:
		import sping.PS as piddlePS
	except ImportError:
		pass
	try:
		import sping.PDF as piddlePDF
	except ImportError:
		pass
	try:
		import sping.PIL as piddlePIL
	except ImportError:
		pass
	try:
		import sping.SVG as piddleSVG
	except ImportError:
		pass
	try:
		import sping.TK as piddleTK
	except ImportError:
		pass
	try:
		import sping.WX as piddleWX
	except ImportError:
		pass
	# from sping.pid import StateSaver
	Font = sping.pid.Font
	try:
		import sping.stringformat as stringformat
	except ImportError:
		pass
else:
	# from piddle import *
	colors = piddle
	Font = piddle.Font
	import piddlePS
	import piddlePDF

	# try:
		# import piddleWX
	# except ImportError:
		# pass

	try:
		import piddleVCR
	except ImportError:
		pass

	try:
		import piddleTK
	except ImportError:
		pass

	try:
		import piddleQD
	except ImportError:
		pass

	try:
		import piddlePIL
	except ImportError:
		pass

	try:
		import piddleGL
	except ImportError:
		pass

	try:
		import piddleSVG
	except ImportError:
		pass

	try:
		import piddleSVG
	except ImportError:
		pass

	import piddleFIG
	import piddleAI
	import stringformat

del _s
