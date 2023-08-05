

class AlignChar(object):
	def __init__(self, c='.'):
		self.c = c
	def align(self, text):
		if len(text) == 0:
			return 0.5

		try:
			idx = text.index(self.c)
		except ValueError:
			return 1.0
		return (0.5+idx)/len(text)


DECIMAL = AlignChar('.')
LEFT='LEFT'
RIGHT='RIGHT'
CENTER='CENTER'
TOP='TOP'
BOTTOM='BOTTOM'


X,Y,Z = 0,1,2


AUTO = 'AUTO'
UNSPECIFIED = -1	# OFI: use this instead of None to mean "unspecified"!

MIN = 0
MAX = 1

LINEAR = 1

SOLID='SOLID'
DASHED='DASHED'
