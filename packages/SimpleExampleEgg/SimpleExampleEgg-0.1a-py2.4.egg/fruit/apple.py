import sys

def doConsole(): print make_pie('CONSOLE')

def make_pie(who):
	"""
>>> import apple as a
>>> a.make_pie('Todd')
'Todd likes pie!!!'
	"""
	return '%s likes pie!!!'%who
#
def _test():
	import doctest
	return doctest.testmod()
#
if __name__ == "__main__":
    _test()
    if len(sys.argv)>1: print make_pie(sys.argv[1])
