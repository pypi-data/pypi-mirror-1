#example method with doctest compatible docstring
def squeeze_me():
	"""
>>> import orange as o
>>> o.squeeze_me()
'have some orange juice!'
	"""
	return 'have some orange juice!'
#
def _test():
	import doctest, orange
	return doctest.testmod(orange)
#
if __name__ == "__main__":
	_test()

