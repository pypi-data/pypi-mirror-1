"""compactpath algorithm

compacts a filepath to fit into a desired length by replacing chars with ellipsis. the funktion 
preserves the last component of the filepath as long as possible. assumption is that this component 
is of major importance for the user.
"""

import os
#****************************************************************************************************
# consts
#****************************************************************************************************
ELLIPSIS = '...'

#****************************************************************************************************
# helpers
#****************************************************************************************************
def rtrunc(n, chars, ellipsis=ELLIPSIS):
	"""truncates a string  to from the right to the desired number of chars, replacing chars with ellipsis
	
	@param n: (int) desired number of truncated chars
	@param chars: (str) chars to truncate
	@param ellipsis: (str) ellipsis to use for char substitution
	@return: (str) the truncated string
	
	>>> rtrunc(4, 'abcd')
	'...d'
	
	>>> rtrunc(99, 'abc')
	'...'
	
	>>> rtrunc(1, 'abc')
	'.'
	
	>>> rtrunc(0, 'abc')
	''
	
	>>> rtrunc(-1, 'abc')
	''
	
	>>> ellipsis = '01234'
	>>> for n in range(len(ellipsis), 0, -1):
	...     rtrunc(n, ellipsis, ellipsis=ellipsis)
	'01234'
	'1234'
	'234'
	'34'
	'4'
	"""
	if n > len(chars):
		n = len(chars)
	if n < 0:
		n = 0
	x = len(ellipsis) - n
	if x < 0:
		x = 0
	e = ellipsis[x:]
	return e + chars[len(chars) - n + len(e): ]
	

def ltrunc(n, chars, ellipsis=ELLIPSIS):
	"""truncates a string  to from the left to the desired number of chars, replacing chars with ellipsis
		
	@param n: (int) desired number of truncated chars
	@param chars: (str) chars to truncate
	@param ellipsis: (str) ellipsis to use for char substitution
	@return: (str) the truncated string
	
	>>> ltrunc(4, 'abcd')
	'a...'
	
	>>> ltrunc(99, 'abc')
	'...'
	
	>>> ltrunc(1, 'abc')
	'.'
	
	>>> ltrunc(0, 'abc')
	''
	
	>>> ltrunc(-1, 'abc')
	''
	>>> ellipsis = '01234'
	>>> for n in range(len(ellipsis), 0, -1):
	...     ltrunc(n, ellipsis, ellipsis=ellipsis)
	'01234'
	'0123'
	'012'
	'01'
	'0'
	"""
	if n > len(chars):
		n = len(chars)
	if n < 0:
		n = 0
	e = ellipsis[:n]
	return chars[ :n - len(e)] + e

#************************************************************************************************
#
#************************************************************************************************
#NOTE:
# a nicer but more complicated (and slower) implementation would preserve
# components more intelligently. e.g. the emidiate parent component of the 
# last component would be preserved longer than some intermediate component

def compactpath(w, fpath, measure=len, ellipsis=ELLIPSIS, path_module=os.path):
	"""compacts a filepath to fit into a desired width
	
	@param fpath: (str) filepath to compact 
	@param measure: function to measure length of the filepath. the function
	should take one parameter: the filepath and should return its length
	@param ellipsis: (str) ellipsis to use for char substitution
	@param path_module: path module to use to split and join filepath
		
	@note: you can always assume that on return measure(fpath) is < w
	for measure(fpath) > 0
	
	
	>>> import posixpath
	>>> compactpath(10, '/aaa/bbb/ccc', path_module=posixpath)
	'/a.../ccc'
	
	>>> compactpath(0, '', path_module=posixpath)
	''
	
	>>> compactpath(-1, '', path_module=posixpath)
	''
		
	>>> p = 'aaa/bbb/ccc'
	>>> for n in range(len(p), 0, -1):
	...     compactpath(n, p, path_module=posixpath)
	'aaa.../ccc'
	'aa.../ccc'
	'a.../ccc'
	'.../ccc'
	'...ccc'
	'...cc'
	'...c'
	'...'
	'..'
	'.'
	''
	"""
	if measure(fpath) < w:
		return fpath
	
	if w > 0:
		head, tail = path_module.split(fpath)
		n = len(head)
		
		while n >= len(ellipsis):
			head = ltrunc(n, head, ellipsis=ellipsis)
			n -= 1
			fpath = path_module.join(head, tail)
			if measure(fpath) < w:
				return fpath
			
		if head == ellipsis:
			tail = ellipsis + tail
			n = len(tail) - 1
		elif head:	
			tail = path_module.join(head, tail, ellipsis=ellipsis)
			n = len(tail)
		else:
			n = len(tail)
				
		while tail:
			if measure(tail) < w:
				return tail
			tail = rtrunc(n, tail)
			n -= 1
		
	return ''
		
#************************************************************************************************
#
#************************************************************************************************
if __name__ == '__main__':
	import doctest
	print 'doctests failed: %s/%s' % doctest.testmod()
