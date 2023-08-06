"""Module to parse and create lines in "a=v;" format.
Normally, the entry points are parse() and concoct().
"""

from gmisclib import gpk_writer
from gmisclib import g_encode
from gmisclib import die

__version__ = "$Revision: 1.21 $"

BadFormatError = g_encode.BadFormatError
_default_encoder = g_encode.encoder()



fwd = _default_encoder.fwd
back = _default_encoder.back


def parse(s, sep=';'):
	"""Parses a line in a=v; a=v form into a dictionary.
	The line may be terminated by a '#' followed by an arbitrary
	comments.    Both attributes and values are assumed to be
	encoded with the default L{g_encode} encoder.  (However, the
	comment is not assumed to be encoded.)

	@param s: the string to be parsed.
	@param sep: (optional) lets you choose the character
		that separates attribute-value pairs.
	@return: dictionary containing a=v pairs.   One special
		entry for comments: "_COMMENT".
	"""
	rv = {};
	if '#' in s:
		ss, c = s.split('#', 1)
		cs = c.strip()
		if cs:
			rv['_COMMENT'] = cs
		if not ss:
			return rv
	else:
		ss = s
	for av in ss.split(sep):
		try:
			a, v = av.split('=', 1)
		except ValueError:	# need more than 1 value to unpack
			# It's OK if it is entirely whitespace...
			if av.strip():
				raise BadFormatError, 'no equals sign in "%s"' % str(av)
		else:
			rv[a.strip()] = back(v.strip())
	return rv


def concoct(s):
	"""Converts a dictionary to a line in the form a=v;a=v;#comment.
	It returns a string.   The entries in the dictionary will be
	converted to a string representation by fwd()."""
	c = None
	l = []
	kvl = s.items()
	kvl.sort()
	for (k,v) in kvl:
		if k == '_COMMENT':
			c = str(v)
		else :
			l.append('%s=%s;' % (k, fwd(v)));
	if c is not None:
		l.extend( [ '#', c ] )
	return ' '.join(l)


def read(fd, sep=';', line=None):
	"""Read a file in a=v; format.
	If line is set, put the line number into a slot with the specified name.
	@return: (data, comments) where data=[{a:v, ...}, ...] and comments=[str, ...]
	@rtype: tuple(list(dict), list(str))
	"""
	comments = []
	data = []
	line_num = 0
	# while True:
	for l in fd:
		line_num += 1
		# l = fd.readline()
		# if l == '':
			# break
		if l.startswith('#'):
			c = l[1:].strip()
			if c != '':
				comments.append(c)
			continue
		if not l.endswith('\n'):
			die.warn('avio.read(): ignoring line without newline.')
			continue
		l = l.strip()
		if l == '':
			continue
		tmp = parse(l, sep)
		if line is not None:
			tmp[line] = line_num
		data.append( tmp )
	return (data, comments)


def test1():
	d = {}
	d['test'] = 'george'
	d['fred'] = 'rrr;;#='
	d['mt'] = ''

	o = parse(concoct(d) + " # comment")

	assert o['test'] == 'george'
	# print "o['fred']=", o['fred']
	assert o['fred'] == 'rrr;;#='
	assert o['mt'] == ''


class writer(gpk_writer.writer):
	__doc__ = """Write a file in a=v; format.
			"""

	def comment(self, comment):
		"""Add a comment to the data file."""
		self.fd.write("# %s\n" % comment)

	def header(self, k, v):
		"""NOTE: this is not a fully general function.
		Keys may not have spaces or equals signs in them.
		Note also that reading of headers from a=v; files
		is not supported.
		"""
		self.fd.write("# %s = %s\n" % (k, fwd(v)))
	
	def __init__(self, fd):
		gpk_writer.writer.__init__(self, fd)

	def datum(self, data_item):
		self.fd.writelines( [ concoct(data_item), '\n'] )



def read_hdc(fd, sep=';', line=None):
	"""This emulates fiatio.read().
	@return: (header, data, comments) where data=[{a:v, ...}, ...] and comments=[str, ...]
	@rtype: tuple(dict, list(dict), list(str))
	"""
	d, c = read(fd, sep=sep, line=line)
	if d:
		h = d[0].copy()
	else:
		h = {}
	for datum in d:
		for (k, v) in h.items():
			if k in datum and datum[k]!=v:
				del h[k]
	hk = h.keys()
	for datum in d:
		for k in hk:
			del d[k]
	return (h, d, c)



def test2():
	import StringIO
	fd = StringIO.StringIO()
	w = writer(fd)
	w.comment('foo')
	w.datum( {'a':'z', 'q':'u'} )
	w.close()
	fd.seek(0)
	d, c = read(fd)
	assert c == ['foo']
	assert len(d) == 1
	assert d[0]['a'] == 'z'
	assert d[0]['q'] == 'u'


if __name__ == '__main__' :
	assert back(fwd('hello \n!@;==')) == 'hello \n!@;=='
	test1()
	test2()
	print "OK: passed tests"
	# print concoct({'x': "a=b;"})
