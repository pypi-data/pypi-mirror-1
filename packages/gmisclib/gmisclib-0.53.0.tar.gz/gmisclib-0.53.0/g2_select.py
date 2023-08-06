import die
import avio
import math
try:
	import load_mod
except ImportError:
	pass

"""This lets you select lines from a list of dictionaries
by means of a little snippet of python code.
It can be used to select lines in a fiat or avio format file
(as read in by fiatio.read or avio.read).
"""

def filterlist(s, d):
	"""This filters a list of lines, passing ones where
	the selector returns true.
	S is the selector -- a little snippet of python,
	and d is the list of data : a list of {k:v} mappings.
	"""
	o = []
	nne = 0
	try:
		for (i,t) in enumerate(d):
			# The value of 'i' is important if there is an exception.
			if  evaluate(s, t):
				o.append(t)
	except NameError, x:
		die.warn('Name Error: %s on item %d: %s' % (str(x), i+1, avio.concoct(t)))
		nne += 1

	for t in d[i+1:]:
		# Only entered if there is a NameError
		try:
			if  evaluate(s, t):
				o.append(t)
		except NameError, x:
			nne += 1
	if nne == len(d):
		die.warn('Name Error on each of the %d data.' % nne)
	return o


def filter_iter(s, d):
	"""This filters a list of lines, passing ones where
	the selector returns true.
	S is the selector -- a little snippet of python,
	and d is the list of data : a list of {k:v} mappings.
	"""
	nne = 0
	try:
		for (i,t) in enumerate(d):
			# The value of 'i' is important if there is an exception.
			if  evaluate(s, t):
				yield(t)
	except NameError, x:
		die.warn('Name Error: %s on item %d: %s' % (str(x), i+1, avio.concoct(t)))
		nne += 1

	for t in d[i+1:]:
		# Only entered if there is a NameError
		try:
			if  evaluate(s, t):
				yield(t)
		except NameError, x:
			nne += 1
	if nne == len(d):
		die.warn('Name Error on each of the %d data.' % nne)


def _compact(s):
	if len(s) > 15:
		return s[:12] + "..."
	return s


class selector_c(object):
	def __init__(self, code, global_values=None):
		"""Code = a string containing python code.
		Global_values = a dictionary containing values to be used by
		that python code.  Note that the dictionary is not copied,
		so that it is shared and changes will be noticed.
		"""
		self.set_code(code)
		if global_values is None:
			self.g = {'math': math}
			try:
				self.g['load_mod'] = load_mod
			except NameError:
				pass
		else:
			self.g = global_values
		self.traptuple = ()
		self.trapmap = []

	def set_code(self, code):
		self.cc = compile(code, '<g2_select: %s>' % _compact(code), 'eval')

	def set_trap(self, exc, result):
		self.traptuple = self.traptuple + (exc,)
		self.trapmap.append( (exc, result) )

	def eval(self, locals):
		try:
			return eval(self.cc, self.g, locals)
		except self.traptuple, x:
			for (e,r) in self.trapmap:
				if isinstance(x, e):
					return r
			raise

	def globals(self, s):
		exec s in self.g


CCSZ = 100
_ccache = {}
def _compile(s):
	# print 'Compile', s
	try:
		selector = _ccache[s]
	except KeyError:
		if len(_ccache) > CCSZ:
			_ccache.pop()
		_ccache[s] = selector_c(s)
		selector = _ccache[s]
	return selector


def accept(s, d):
	"""This checks a single dictionary, and returns
	the result of the selector.   Errors in the evaluation
	are trapped and cause accept() to return False.
	S is the selector -- a little snippet of python,
	and d is the data : a {k:v} mapping.
	"""
	try:
		return evaluate(s, d)
	except NameError, x:
		die.warn('Name Error: %s on %s in %s' % (str(x), avio.concoct(d), s))
	return False


def whynot(s, d):
	"""Returns an explanation of why d was not accepted, given s, or None of d was accepted."""
	try:
		if _compile(s).eval(d):
			return None
		else:
			return "Sorry, not implemented yet."
	except NameError, x:
		return "data does not contain attribute=%s (d=%s) (selector=%s)" % (x.args[0],
								_compact(avio.concoct(d)),
								_compact(s)
								)

def why(s, d):
	"""Returns an explanation of why d was accepted, given s, or None if d was not accepted."""
	if not accept(s, d):
		return None
	return "Sorry, not implemented yet."


def evaluate(s, d):
	"""This checks a single dictionary, and returns
	the result of the selector.
	S is the selector -- a little snippet of python,
	and d is the data : a {k:v} mapping.
	"""
	return _compile(s).eval(d)


def test():
	x = selector_c('y')
	assert x.eval( {'y': 1} ) == 1
	try:
		x.eval( {} )
	except NameError:
		pass
	else:
		assert 0, 'Whoops! no exception when one was expected.'
	z = selector_c('y+w', {'w':1})
	assert z.eval( {'y': 1} ) == 2
	z.globals('w=2')
	assert z.eval( {'y': 1} ) == 3
	x = selector_c('y')
	x.trap(NameError, 44)
	assert x.eval({}) == 44



if __name__ == '__main__':
	test()
