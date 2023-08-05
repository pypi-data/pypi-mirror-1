import die
import Num


try:
	import TableIO
except ImportError:
	TableIO = None


_lm = {'dotted' : (0.04, 0.1), 'dot': (0.04, 0.1), 'finedot': (0.02, 0.1),
	'broken' : (0.04, 0.8), 'dashed' : (0.04, 0.5),
	'solid' : (0.04, 1.0)
	}

def ls(s):
	per = (hash(s + 'period')/3) % 100
	onfrac = (hash(s + 'onfrac')/5) % 100
	return {'period': per/100.0, 'onfrac': onfrac/100.0}


def getline(s):
	a = s.strip().split(',')
	if len(a) == 2:
		try:
			per = float(a[0])
			on = float(a[1])
		except:
			return ls(s)
		if 0<=per<1.0 and 0<=on<=1.0:
			return {'period': per, 'onfrac': on}
		return ls(s)
	if _lm.has_key(s):
		return {'period': _lm[s][0], 'onfrac': _lm[s][1]}
	return ls(s)


def py_read(fd):
	nf = None
	n = 0
	o = []
	for l in fd.readlines():
		n += 1
		l = l.strip()
		if l == '':
			continue
		l = l.split('#')[0]
		if l == '':
			continue
		a = l.split()
		if nf is None:
			nf = len(a)
		if len(a) != nf:
			die.die('Line %d has a different length from previous.' % n)
		o.append( [ float(t) for t in a ] )
	return Num.array(o, Num.Float)


class dataclass(object):
	def __init__(self, a):
		self.a = a
	
	def column(self, c):
		if c == 't' or c=='i':
			return Num.arrayrange(self.a.shape[0])
		c = int(c)
		if c >= 0:
			return self.a[:,c]
		return Num.arrayrange(self.a.shape[0])


def read(f):
	import sys

	if f == '-':
		return dataclass(py_read(sys.stdin))

	if TableIO is not None:
		return dataclass(TableIO.readTableAsArray(f, '#'))
	return dataclass(py_read(open(f, 'r')))
