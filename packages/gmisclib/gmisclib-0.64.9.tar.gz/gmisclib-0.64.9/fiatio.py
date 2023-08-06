"""Fiatio reads and writes the simple
FIAT file format (dwittman@bell-labs.com,
http://dls.bell-labs.com/fiat/fiat.html).  FIAT is
nice because all the header information looks like a comment
to most programs, so they will treat a FIAT file as
simple multi-column ASCII.

This describes fiat 1.1 format, which is nearly 100%
upwards compatible with fiat 1.0 format.
It is defined as follows:

Lines are separated by newlines.

All values are encoded by replacing newline and other difficult
characters by a percent character (%) followed by a hex code
on writing, and the reverse on reading.

At the top of the file, you have a line identifying the format: "# fiat 1.1"
(regexp: "# fiat 1\.[0-9.]+").

Then, you have any number of header lines beginning with "#".
Header lines are in the form "# attribute = value" (where
white space is optional and can be a mixture of spaces and tabs).
The attribute must match [a-zA-Z_][a-zA-Z_0-9]* .
The value is whatever follows the equals sign, after leading and following
white space is stripped.  If the value begins and ends with
the same quote character ['"], the quotes are also stripped off.
Values may contain any character except newline and the chosen quote.
Note that you must quote or encode a value if it begins or ends with whitespace.

Any other header lines are just treated as comments and ignored.

There may be lines in the header of the form
"# TTYPEn = name" or "#ttype4 = name"
which name the columns of the data (the leftmost column is TTYPE1).
If you don't name the nth column, its name will be "n".
When writing, this module adds an attribute
COL_SEPARATOR which contains the numeric code(s)
(ASCII) of the column separator character(s).
The module also adds a COL_EMPTY attribute with the string used to mark an
blank item.  However, all attributes and names are optional.

Finally, the header is followed by multicolumn ASCII data.
Columns are separated (by default) with any white space,
but if there is a COL_SEPARATOR attribute, it is used instead.
Empty entries for columns should be indicated by whatever code is specified
in COL_EMPTY, if that is set.
Otherwise, if COL_SEPARATOR is set, COL_SEPARATOR strings separate items,
some of which may simply be empty.
(In all cases, a completely blank line is treated as a datum which as all
columns empty.)

If there is no DATE attribute, the write routine adds one, using the current date
and time, in the form ccyy-mm-ddThh:mm:ss (as defined in the NASA FITS format).

This is not quite DWittman FIAT (1.0), which forces value to either be quoted
or to contain no white space. Dwittman FIAT will take a line
in the form "#a=b c", and interpret c as a comment, whereas
fiat 1.1 will interpret "b c" as the value.
However, almost all files will be interpreted the same way.

Here's an example:
# fiat 1.1
# TTYPE1 = b
# TTYPE2 = a
# SAMPRATE = 2.3
# DATE = 2001-09-21T21:32:32
# COL_EMPTY = "%na"
# COL_SEPARATOR = "9"
# Comment1
# Comment2
# b	a
2	1
3	2
3	%na
%na	3
%na	%na
0	1
"""


import re
import types
import string
from gmisclib import gpk_writer
from gmisclib import g_encode
from gmisclib import die

__version__ = "$Revision: 1.53 $"


TABLEN = 8




def _alph(s):
	n = min(len(s), 8)
	o = 0.0
	f = 1.0
	# Not OK for unicode. Sigh.
	for i in range(n):
		f = f/256.0
		o += f * ord(s[i])
	return -o


# def col_order(a, b):
	# lc = cmp(len(str(a[0]))+a[1], len(str(b[0]))+b[1])
	# if lc != 0:
		# return lc
	# return cmp(str(a[0]), str(b[0]))

def col_order(a, b):
	sa = str(a)
	sb = str(b)
	lc = cmp(len(sa), len(sb))
	if lc != 0:
		return lc
	return cmp(sa, sb)


_autogen = re.compile("COL_SEPARATOR$", re.IGNORECASE)
_drop = re.compile("(__NAME_TO_COL|__COLUMNS)$")


def write_array(fd, adata, columns=None, comments=None, hdr=None, sep='\t', numeric=False):
	"""Write a rectangular array in FIAT format.
	Adata is a 2-D numpy array or a sequence of sequences.
	"""
	w = writer(fd, sep=sep)

	if columns is not None:
		w.add_cols(columns)
	if hdr is not None:
		w.headers(hdr)
	if comments is not None:
		for c in comments:
			w.comment(c)
	for i in range(len(adata)):
		w.datavec( adata[i], numeric=numeric )


_autogen = re.compile("TTYPE[0-9]+|COL_EMPTY|COL_SEPARATOR", re.IGNORECASE)

def write(fd, ldata, comments=None, hdr=None, sep='\t', blank='%na', fixed_order=0):
	"""Write a file in FIAT format.
			Ldata is a list of dictionaries.  Each dictionary
			corresponds to one line in the file.   Each
			unique key generates a column, and the values
			are printed in the data section of the FIAT file.
			Note that the TTYPE header lines will be automatically
			generated from ldata.
			Hdr is a dictionary of information that will be
			put in the header.
			Comments is a list of comment lines for the header.
			Fd is a file descriptor where the data should be
			written.
			Sep is a string used to separate data columns.
			Blank is a string to use when a data value is missing.
		"""
	w = writer(fd, sep=sep, blank=blank)
	if comments is not None:
		for com in comments:
			w.comment(com)
	if hdr is not None:
		w.headers(hdr)
	for d in ldata:
		w.datum(d)
	fd.flush()
	# os.fsync(fd.fileno())


class writer(gpk_writer.writer):
	__doc__ = """Write a file in FIAT format.
			Ldata is a list of dictionaries.  Each dictionary
			corresponds to one line in the file.   Each
			unique key generates a column, and the values
			are printed in the data section of the FIAT file.
			Note that the TTYPE header lines will be automatically
			generated from ldata.
			Hdr is a dictionary of information that will be
			put in the header.
			Comments is a list of comment lines for the header.
			Fd is a file descriptor where the data should be
			written.
			Sep is a string used to separate data columns.
			Blank is a string to use when a data value is missing.
			"""

	def comment(self, comment):
		"""Add a comment to the data file."""
		if '\n' in comment:
			raise ValueError, "No newline allowed in comments for fiatio."
		self.fd.write("# %s\n" % comment)


	def header(self, k, v):
		if _autogen.match(k):
			die.warn("Hdr specifies information that is automatically generated: %s" % k)
		elif _drop.match(k):
			return
		self._write_header(k, v)
	

	def __init__(self, fd, sep='\t', blank='%na'):
		gpk_writer.writer.__init__(self, fd)
		self.enc = _encoder(sep)
		self.blank = blank
		self.sep = sep
		self.map = {}
		self.columns = []
		fd.write("# fiat 1.2\n")
		self._write_header('COL_EMPTY', self.blank)
		self._write_header('COL_SEPARATOR', 
		 		' '.join([str(ord(sc)) for sc in self.sep])
				)

	def add_cols(self, colnames):
		n = len(self.map)
		for c in colnames:
			self.map[c] = n
			self.columns.append( c )
			self.fd.write("# TTYPE%d = %s\n" % (n+1, c))
			n += 1
	
	def _hline(self, o):
		"""o is not used, except to help set the width of each field.
		"""
		ostart = 0
		hstart = 1	# The comment symbol.
		ls = len(self.sep)
		hline = []
		for (cn, val) in zip(self.columns, o):
			w = max(1, len(val) + (ostart - hstart)/2)
			ostart += len(val) + ls
			cn = str(cn)
			hstart += len(cn) + ls
			hline.append(cn.center(w))
		self.fd.write('#' + self.sep.join(hline) + '\n')


	def _write_header(self, k, v):
		v = '%s' % v
		if '\n' in v or v[0] in string.whitespace or v[-1] in string.whitespace:
			v = '|%s|' % self.enc.fwd(v)
		self.fd.write("# %s = %s\n" % (k, v))


	def datum(self, data_item):
		o = [ self.blank ] * len(self.map)
		# o = [ self.blank for q in self.map.keys() ]
		try:
			# This is the path for most calls.
			for (k, v) in data_item.iteritems():
				o[self.map[k]] = self.enc.fwd(str(v))
		except KeyError:
			# This is the path the first time, when self.map
			# doesn't yet exist.
			add = []
			for (k, v) in data_item.iteritems():
				if isinstance(k, types.StringType):
					pass
				elif isinstance(k, types.IntType) and k>=0:
					pass
				else:
					raise TypeError, ("Key is not a string or non-negative integer", k)
				if not k in self.map:
					# add.append( (k, len(str(v))) )
					add.append( k )
			add.sort(col_order)
			# self.add_cols([ t[0] for t in add ])
			self.add_cols( add )
			o = [ self.blank ] * len(self.map)
			# o = [ self.blank for q in self.map.keys() ]
			for (k, v) in data_item.iteritems():
				o[self.map[k]] = self.enc.fwd(str(v))
			self._hline(o)
		self.fd.write(self.sep.join(o) + '\n')


	def datavec(self, vector, numeric=False):
		"""This assumes that you've already called add_cols() to set the
		column names.   It is an error to have a vector whose length doesn't
		match the number of column names.
		"""
		lv = len(vector)
		lc = len(self.columns)
		assert lv >= lc, "vector length=%d but %d columns" % (lv, lc)
		if lc < lv:
			self.add_cols( [ '%d' % q for q in range(lc, lv) ] )
		if numeric:
			self.fd.write( self.sep.join([str(q) for q in vector]) + '\n' )
		else:
			self.fd.write( self.sep.join([self.enc.fwd(str(q)) for q in vector]) + '\n' )


class merged_writer(writer):
	"""Assumes that the data will be read with read_merged(), so that
	header values will supply default values for each column.
	"""

	def __init__(self, fd, sep='\t', blank='%na'):
		writer.__init__(self, fd, sep, blank)
		self._hdr = {}
	
	def header(self, k, v):
		self._hdr[k] = v
		writer.header(self, k, v)

	def datum(self, data_item):
		"""Assumes that the data will be read with read_merged(), so that
		header values will supply default values for each column.
		This writes a line in the fiat file, but first it deletes any values
		that alread exist as a header item of the same name.
		"""
		tmp = {}
		for (k, v) in data_item.items():
			if k not in self._hdr or v!=self._hdr[k]:
				tmp[k] = v
		writer.datum(self, tmp)




BadFormatError = g_encode.BadFormatError
FiatError = BadFormatError


class ConflictingColumnSpecification(BadFormatError):
	def __init__(self, s):
		FiatError.__init__(self, s)



def _check_last_comment(comment, names):
	"""Check to see if the last comment is just a list of column names.
	This is what write() produces.   If so, it can be safely deleted.
	"""
	# print "SORTED NAMES=", sorted_names
	# print "LAST COMMENT", comment.split()
	return comment.split() == names



_encoder_cache = {}
def _encoder(sep):
	if not sep in _encoder_cache:
		if len(_encoder_cache) > 30:
			_encoder_cache.pop()
		notallowed = ' \t%\n\r'
		if sep is not None and sep not in notallowed:
			notallowed += sep
		_encoder_cache[sep] = g_encode.encoder(notallowed=notallowed)
	return _encoder_cache[sep]


class rheader(object):
	LTTYPE = len('TTYPE')

	def __init__(self):
		self.sep = None
		self.blank = '%na'
		self.comments = []
		self.name_to_col = {}
		self.header = {}
		# self.header = {'__COLUMNS': {}, '__NAME_TO_COL': {}
				# }
		self.enc = _encoder('')
		self.icol = []
		self.colmap = {}

	def dequote(self, s):
		"""Remove quotes from a value."""
		ss = s.strip()
		if len(ss) < 2:
			return ss
		elif ss[0] in '\'"|' and ss[0]==ss[-1]:
			if ss[0] == '|':
				return self.enc.back(ss[1:-1])
			return ss[1:-1]
		return ss
	
	def parse(self, s):
		l = s[1:].strip()
		a = l.split('=', 1)
		if len(a) > 1 and len(a[0].split()) == 1:
			attr = a[0].strip()
			val = self.dequote(a[1])
			if attr.upper().startswith('TTYPE'):
				ic = int(attr[self.LTTYPE:])-1
				if ic in self.colmap and self.colmap[ic]!=val:
					raise ConflictingColumnSpecification, 'column=%d: "%s" vs. "%s"' % (
										ic, val, self.icol[ic]
										)
				if val in self.name_to_col and self.name_to_col[val] != ic:
					raise ConflictingColumnSpecification, 'val="%s": columns %d vs. %d' % (
										val, ic, self.icol[ic]
										)
				self.extend_icol(ic+1)
				self.icol[ic] = val
				self.colmap[ic] = val
				self.name_to_col[val] = ic
			elif attr == 'COL_EMPTY':
				self.blank = val
			elif attr == 'COL_SEPARATOR':
				self.sep = ''.join( [chr(int(q)) for q in val.split() ] )
				self.enc = _encoder(self.sep)
			else:
				self.header[attr] = val
		elif not _check_last_comment(l, self.icol):
			self.comments.append(l)


	def extend_icol(self, la):
		if len(self.icol) < la:
			self.icol.extend( range(len(self.icol), la) )

	def dump(self, d):
		hdr = self.header
		com = self.comments
		self.header = {}
		self.comments = []
		return (hdr, d, com)

	def dumpx(self, d):
		hdr = self.header
		hdr['__NAME_TO_COL'] = self.name_to_col
		hdr['__COLUMNS'] = self.colmap
		com = self.comment
		self.header = {}
		self.comment = []
		return (hdr, d, com)

def read(fd):
	"""Read in a fiat file. Return (header, data, comments),
	where header is a dictionary of header information,
	data is a list of dictionaries, one for each line in the file,
	and comments is a list of strings.
	Each line in the FIAT file is represented by a dictionary that maps
	column name into the data (data is a string).
	Lines without data in a certain column will not have an entry in that line's
	dictionary for that column name.
	Two special entries are added to header: __COLUMNS points to a mapping
	from column numbers (the order in which they appeared in the file,
	left to right, starting with 0) to names,
	and __NAME_TO_COL is the reverse mapping.

	Note that this routine requires all header lines to precede all data
	lines.    Fiat does not make that requirement.
	"""
	out = []
	hdr = {}
	comments = []
	for (h, d, c) in readiter(fd):
		hdr.update(h)
		comments.extend(c)
		if d is not None:
			out.append(d)
	return (hdr, out, comments)


def read_merged(fd):
	"""Read in a fiat file. Returns (among other things)
	a list of dictionaries, one for each line in the file.
	Each line in the input FIAT file is represented by a dictionary that maps
	column name into the data (data is a string).
	The header data in the FIAT file is merged into the per-column data,
	so that the header data is used as a default value for a column.
	In fact, each header value creates a column of the same name, so that all
	the information in the file is in the resulting list of dictionaries.

	That this routine does not require header lines to precede data lines.
	If header lines appear in the middle, then a new column will be created from
	that point onwards.
	@return: (data, comments)
	@rtype: (list(dict), list(str))
	@param fd: Where the data comes from.
	@type fd: file
	"""
	out = []
	comments = []
	hdr = {}
	for (h, d, c) in readiter(fd):
		comments.extend(c)
		if d is not None:
			hdr.update(h)
			tmp = hdr.copy()
			tmp.update(d)
			out.append(tmp)
	return (out, comments)



def readiter(fd):
	"""Read in a fiat file.
	Each line in the file is represented by a dictionary that maps
	column name into the data (data is a string).
	Lines without data in a certain column will not have an entry in that line's
	dictionary for that column name.
	A fiat file is a mixed header/data file.   Typically, all
	the header info is at the top, but it can be intermixed in with
	the data.    (Lines beginning with '#' are either header data
	or comments.)

	@param fd: A file descriptor to read.
	@type fd: file object
	@return: (header, data, comments),
		where header is the collected dictionary of header information
		since the last iteration,
		data is a dictionary of the data on the current line,
		and comments is a list of comment string seen so far.
		The end of the file yields None for the last data,
		along with any header info or comments after the last datum.
	@rtype: (dict(str:str), dict(str:str), list(str))
	"""
	hobj = rheader()

	line = fd.readline()
	if line.startswith('# fiat'):
		line = fd.readline()
	while line:
		line = line.rstrip('\r\n')

		if line.startswith('#'):
			hobj.parse(line)
		elif not line:		# empty line
			yield hobj.dump({})
		else:
			a = line.split(hobj.sep)
			if len(hobj.icol) < len(a):
				hobj.extend_icol(len(a))
			tmp = {}
			for (ic, ai) in zip(hobj.icol, a):
				if ai != hobj.blank:
					tmp[ic] = hobj.enc.back(ai)
			yield hobj.dump(tmp)
		line = fd.readline()
	yield hobj.dump(None)



def read_as_float_array(fd, loose=False, baddata=None):
	"""Read in a fiat file. Return (header, data, comments),
	where header is a dictionary of header information,
	data is a numpy array, and comments is a list of strings.
	Two special entries are added to header: __COLUMNS points to a mapping
	from column numbers (the order in which they appeared in the file,
	left to right, starting with 0) to names, and
	_NAME_TO_COL holds the reverse mapping.

	Empty values are set to NaN.

	If loose==False, then all entries must be either floating point numbers
	or empty entries or equal to baddata (as a string, before conversion
	to a float).
	If loose==True, all non-floats will simply be masked out.
	"""
	import Num
	import fpconst

	if loose:
		def float_or_NaN(s):
			if s == baddata:
				tmpd = NaN
			else:
				try:
					tmpd = float(s)
				except ValueError:
					tmpd = NaN
			return tmpd
	else:
		def float_or_NaN(s):
			if s == baddata:
				tmpd = NaN
			else:
				tmpd = float(s)
			return tmpd



	NaN = fpconst.NaN
	hobj = rheader()

	data = []
	maxcols = None
	line = fd.readline()
	if line.startswith('# fiat'):
		line = fd.readline()
	while line:
		line = line.rstrip('\r\n')

		if line.startswith('#'):
			hobj.parse(line)
		else:
			a = line.split(hobj.sep)
			if len(hobj.icol) < len(a):
				hobj.extend_icol(len(a))
			tmpd = Num.array( [ float_or_NaN(q) for q in a ], Num.Float)
			data.append(tmpd)
		line = fd.readline()

	# Now, if the length has expanded between the beginning and the end,
	# go back and fill out the data with NaNs to a uniform length.
	if data and data[0].shape[0] < data[-1].shape[0]:
		NaNs = Num.zeros((maxcols,), Num.Float) + NaN
		assert not Num.sometrue(Num.equal(NaNs, NaNs))
	i = 0
	while i<len(data) and data[i].shape[0]<maxcols:
		data[i] = Num.concatenate((data[i], NaNs[:maxcols-data[i].shape[0]]))
		i += 1

	return (hobj.header, data, hobj.comments)



def _hcheck(a, b):
	# del a['__NAME_TO_COL']
	# del a['__COLUMNS']
	assert abs(float(a['SAMPRATE'])-float(b['SAMPRATE'])) < 1e-8
	del a['SAMPRATE']
	del b['SAMPRATE']
	assert a == b


def _dcheck(a, b):
	for (ax, bx) in zip(a, b):
		tmp = {}
		for (k, v) in bx.items():
			tmp[k] = str(v)
		assert ax == tmp


def test1():
	fd = open("/tmp/fakeZZZ.fiat", "w")
	data = [{'a':1, 'b':2},
			{'a':2, 'b':3},
			{'b':3},
			{'a':3},
			{},
			{'a':1, 'b':0}
		]
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001-09-21T21:32:32'}
	write(fd, data, comments, header)
	fd.flush()
	# os.fsync(fd.fileno())
	fd.close()
	fd = open("/tmp/fakeZZZ.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments


def test2():
	fd = open("/tmp/fakeZZZ.fiat", "w")
	data = [{}, {'a': 111},
			{'a':1, 'b':2},
			{'a':2, 'b':3},
			{'b':3},
			{'a':3},
			{},
			{'a':1, 'b':0}
		]
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001-09-21T21:32:32'}
	write(fd, data, comments, header)
	fd.flush()
	# os.fsync(fd.fileno())
	fd.close()
	fd = open("/tmp/fakeZZZ.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments



def test3():
	fd = open("/tmp/fakeZZ1.fiat", "w")
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001/09/21', 'nasty': '\033\032\011\rxebra'}
	data = [
		{'a':101, 'bljljlj':2, 'fd': 33341, 'q': 12},
		{'a':10, 'bljljlj':2, 'fd': 3334111, 'q': 12},
		{'a':10, 'bljljlj':21, 'fd': 3331, 'q': 12},
		{'a':1, 'bljljlj':4, 'fd': 3334122, 'q': 12},
		{'a':1, 'bljljlj':3, 'fd': 333, 'q': 12}
		]
	write(fd, data, comments, header,
		blank = 'NA'
		)
	fd.flush()
	# os.fsync(fd.fileno())
	fd.close()
	fd = open("/tmp/fakeZZ1.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments


def test4():
	import Num
	fd = open("/tmp/fakeZZ1.fiat", "w")
	adata = Num.zeros((4,7), Num.Float)
	for i in range(adata.shape[0]):
		for j in range(adata.shape[1]):
			adata[i,j] = i**2 + 2*j**2 - 0.413*i*j - 0.112*float(i+1)/float(j+2)
	comments = ['C1']
	hdr = {'foo': 'bar', 'gleep':' nasty\n value\t'}
	columns = ['A', 'b', 'C', 'd']
	write_array(fd, adata, columns=columns,
			comments=comments, hdr=hdr, sep='\t')
	fd = open("/tmp/fakeZZ1.fiat", "r")
	h, adtest, c = read_as_float_array(fd, loose=False, baddata=None)
	assert c == comments
	for (k,v) in hdr.items():
		assert h[k] == v
	# for (i,cname) in enumerate(columns):
		# assert h['__COLUMNS'][i] == cname
		# assert h['__NAME_TO_COL'][cname] == i
	if Num.sum(Num.absolute(adtest-adata)) > 0.001:
		die.die('Bad array recovery')

def test():
	test1()
	test2()
	test3()
	test4()

if __name__ == '__main__':
	test()


__author__ = '$Author: gpk $'
__version__ = '$Revision: 1.53 $'
__date__ = '$Date: 2007/06/30 13:31:21 $'
