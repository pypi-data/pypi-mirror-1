"""This is a compatibility kluge to let you say

import colors
 ... colors.black ...

when using either PIDDLE or SPING.
"""

try:
	from sping.colors import *
except:
	from piddle import *
