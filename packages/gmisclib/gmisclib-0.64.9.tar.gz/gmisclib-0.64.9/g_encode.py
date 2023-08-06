"""This module allows strings to be encoded into a
reduced subset.   It is designed to work for avio.py,
and to do a minimal mapping, so that the resulting
text is human-readable.    I suppose that Quoted-Printable
encoding would work, too...
Normally, the entry points are fwd() and back(),
but you can also make custom encoder classes.

Note that there are some twiddly points in defining
encoders -- the notallowed and allowed arguments
need to be thought through carefully, as they are
passed into the re module as part of a regular
expression.    Certain characters may give surprising
results.
"""

import string;
import re


__version__ = "$Revision: 1.10 $"


class BadFormatError(RuntimeError):
	def __init__(self, *x):
		RuntimeError.__init__(self, *x)


_backdict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5,
		'6':6, '7':7, '8':8, '9':9,
		'a':10, 'A':10, 'b':11, 'B':11,
		'c':12, 'C':12, 'd':13, 'D':13,
		'e':14, 'E':14, 'f':15, 'F':15 }


_specials = [ ('mt', ''),
		(' ', '_'),
		('u', '_'),
		('p', '.'),
		('m', ','),
		('s', ';'),
		('z', '='),
		('t', '\t'),
		('Z', '\033'),
		('M', '&'),
		('T', '%'),
		('l', '/'),
		('K', '\\'),
		('k', '\b'),
		('R', '\r'),
		('L', '\n'),
		('q', '"'),
		('Q', '?'),
		('U', "'"),
		('S', ' '),
		('P', '#')
		]


def _expand_bdict(b):
	o = {}
	for (si, ni) in b.items():
		for (sj, nj) in b.items():
			o[si + sj] = chr(16*ni + nj)
	for (k, v) in _specials:
		assert not _backdict.has_key(k), "Special (%s) collides with hex." % k
		assert not o.has_key(k), "Special (%s) collides with hex or special." % k
		o[k] = v
	return o


_bdict = _expand_bdict(_backdict)


_reb = re.compile('%([0-9a-fA-F][0-9a-fA-F]|'
			+ '|'.join([_c[0] for _c in _specials])
			+ ')')




def _fromhex(x):
	"""Expands a %XX code (or the specials above) into a character."""
	# q = x.string[x.start():x.end()]
	q = x.group(1)
	# assert len(q)==3 and q[0]=='%', 'usage: %xx'
	# return chr(_backdict[q[1]]*16 + _backdict[q[2]]);
	return _bdict[q]


def _rm_nl(s):
	if s.endswith('\n'):
		return s[:-1]
	return s



def _expand_fdict():
	o = {}
	for c in range(256):
		o[chr(c)] = '%%%02x' % c
	for (k,v) in _specials:
		o[v] = '%%%s' % k
	return o


_fdict = _expand_fdict()


def _tohex(x):
	"""Converts a single character in a MatchObject to a %xx escape sequence"""
	q = x.string[x.start()]
	assert len(q)==1, 'tohex operates on a single character'
	# return '%%%02x' % ord(q)
	# print "x=", x.string, "q=(%s)" % q
	return _fdict[q]


class encoder:
	def __init__(self, allowed=None, notallowed=None):
		assert not ( allowed is not None and notallowed is not None), "Either allowed or notallowed, not both."
		if notallowed is not None:
			assert '%' in notallowed, "Sorry: cannot allow '%'."
			self.ref = re.compile('(^\s)|([%s])|(\s$)' % notallowed)
		else:
			if allowed is None:
				allowed = string.letters + string.digits + \
						r"""_!@$^&*()+={}[\]\|:'"?/>.<,\ ~`-"""
			assert not '%' in allowed, "Cannot allow '%'."
			self.ref = re.compile('(^\s)|([^%s])|(\s$)' % allowed)


	def back(self, x):
		"""Converts back from a string containing %xx escape sequences to
		an unencoded string.
		"""
		# if x == '%mt':
			# return ''
		try:
			return _reb.sub(_fromhex, x)
		except KeyError, x:
			raise BadFormatError, "illegal escape sequence: %s" % x


	def fwd(self, x):
		"""Escapes a string so it is suitable for a=v; form.
		Nonprinting characters, along with [;#] are converted
		to %xx escapes (hexadecimal).
		Non-strings will be converted to strings with repr(),
		and can be fed back into the python interpreter.  """
		if not isinstance(x, str):
			x = repr(x)
		if x == '':
			return '%mt'
		# print "x=(%s)" % x
		return self.ref.sub(_tohex, x)




def test():
	e = encoder()
	assert e.back(e.fwd('george')) == 'george'
	assert e.back(e.fwd('hello there')) == 'hello there'
	assert e.back('%sfoo') == ';foo'
	assert e.back('%Sfoo%S%P') == ' foo #'
	assert e.back('%Tfoo') == '%foo'
	assert e.back(e.fwd('%hello')) == '%hello'
	assert e.back(e.fwd(' hello there')) == ' hello there'
	assert e.back(e.fwd(' hello there\t')) == ' hello there\t'
	assert e.back(e.fwd(' hello there\t=')) == ' hello there\t='
	assert e.back(e.fwd(' hello there\t=;#')) == ' hello there\t=;#'
	assert e.back(e.fwd(' hello+_there\t=;#')) == ' hello+_there\t=;#'
	assert e.back(e.fwd('hello+_there\t=;#')) == 'hello+_there\t=;#'
	assert e.fwd('hello there') == 'hello there'

	ee = encoder('abcd')
	assert ee.fwd("cab d") == 'cab%Sd'
	assert ee.fwd("e") == '%65'
	assert ee.fwd("aaaa bbbb") == 'aaaa%Sbbbb'

	ee = encoder(notallowed = ']\n\r%')
	assert '\n' not in ee.fwd('hello world\n\r')
	assert ']' not in ee.fwd('hello]% world\n\r')
	assert ee.back(ee.fwd('hello world\n\r'))=='hello world\n\r'



if __name__ == '__main__' :
	test()
	print "OK: passed tests"
