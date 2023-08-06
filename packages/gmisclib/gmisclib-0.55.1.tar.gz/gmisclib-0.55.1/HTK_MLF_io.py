
"""This reads MLF (Master Label Files) for/from the HTK speech recognition
toolkit.
"""

import os.path
import glob
import die
from xwaves_errs import *

TIME_QUANTUM = 1e-7
# At 11025 Hz sampling rate.
# TIME_QUANTUM = 1e-7 * (11025.0/11000.0)

class ReferencedFileNotFound(Error):
	def __init__(self, *s):
		Error.__init__(self, *s)


def _findfile(f, postfix, verbose):
	"""Find a file.   Starting with a glob expression C{f}, strip off
	any .something suffix, then add on C{postfix}.
	If that glob evaluates to a file, return (d,f)
	where C{d} is the directory and C{f} is the filename (with postfix removed).
	Postfix would normally start with '.'.
	At the end, os.path.join(d, f) + postfix will name a file.
	"""
	if not f:
		return (None, None)
	d0, f0 = os.path.split(f)
	f0 = os.path.splitext(f0)[0]
	fx = os.path.join(d0, f0) + postfix
	if verbose:
		die.info("HTK_MLF_io._findfile: glob=%s" % fx)
	gl = glob.glob(fx)
	if verbose:
		die.info("HTK_MLF_io._findfile globs=%s" % ','.join(gl))
	if len(gl) == 0:
		raise ReferencedFileNotFound, fx
	assert len(gl) == 1, 'Too many alternatives for %s: %d' % (fx, len(gl))
	d1, f1 = os.path.split(gl[0])
	# assert f1.endswith(postfix)
	f1 = os.path.splitext(f1)[0]
	# f1 = f1[:-len(postfix)]
	if verbose:
		die.info("HTK_MLF_io._findfile d1=%s d1=%s" % (d1, f1))
	return (d1, f1)


def _get_symbols(fd):
	sym = []
	while True:
		s = fd.readline()
		if s == '':
			# It is legal for the last chunk of a file
			# to end with a blank line, rather than a dot.
			if sym and sym[-1]=='':
				sym.pop()
				break
			else:
				raise BadFileFormatError
		s = s.rstrip('\r\n')
		if s == '.':
			break
		sym.append( s )
	return sym


def _get_threecol(fd, time_quantum):
	sym = []
	while True:
		s = fd.readline()
		if s == '':
			raise BadFileFormatError
		s = s.rstrip('\r\n')
		if s == '':
			# It is legal for the last chunk of a file
			# to end with a blank line rather than a
			# dot.
			if fd.readline() == '':
				break
			else:
				raise BadFileFormatError
		if s == '.':
			break
		t0, te, lab = s.split(None, 2)
		sym.append( (float(t0)*time_quantum, float(te)*time_quantum, lab) )
	return sym


def readiter(mlf_fn, postfix='.wav', datapath='.', strict=True,
		threecol=False, findfile=True, pathedit=None,
		time_quantum=TIME_QUANTUM,
		verbose=False):
	"""Read a MLF file (relevant to HTK took kit).
	Returns [ {'filespec':path, 'd': d, 'f': f, 'symbols': zzz}, ... ]
	where 'd' and 'f' are only present if findfile==True.
	Datapath and pathedit are ways to deal with the
	situation where the MLF file has been moved, or (for other reasons)
	the filenames in the MLF file don't point to the actual data.

	"""
	if pathedit is None:
		pathedit = os.path.join

	dmlf, fmlf = os.path.split(mlf_fn)

	try:
		fd = open(mlf_fn, 'r')
	except IOError, x:
		raise NoSuchFileError(*(x.args))
	l = fd.readline()
	assert l=='#!MLF!#\n', 'l=%s' % l
	i = 0
	while True:
		f = fd.readline()
		f = f.strip()
		if f == '':
			break
		if f.startswith('"') and f.endswith('"'):
			f = f[1:-1]
		fspec = f
		rv = {'filespec': fspec, 'i': i}
		if findfile:
			if verbose:
				die.info("dmlf=%s; datapath=%s; f=%s" % (dmlf, datapath, f))
			try:
				d1, f1 = _findfile(pathedit(dmlf,datapath,f), postfix, verbose)
			except ReferencedFileNotFound, x:
				if strict:
					raise
				else:
					die.warn('No such file: %s from %s' % (x, fspec))
					_get_symbols(fd)
					continue
			else:
				rv['d'] = d1
				rv['f'] = f1
		if threecol:
			rv['symbols'] = _get_threecol(fd, time_quantum)
		else:
			rv['symbols'] = _get_symbols(fd)
		yield rv
		i += 1


def read(mlf_fn, **kw):
	return list( readiter(mlf_fn, **kw) )


class writer(object):
	def __init__(self, mlf_fd, time_quantum=TIME_QUANTUM):
		assert time_quantum > 0.0
		self.fd = mlf_fd
		self.fd.writelines('#!MLF!#\n')
		self.nchunks = 0
		self.scale = 1.0/time_quantum

	def chunk(self, filespec, data):
		if self.nchunks > 0:
			self.fd.writelines('.\n')
		self.fd.writelines( [ '"%s"\n' % filespec,
					'\n'.join(data), '\n'
					]
				)
		self.nchunks += 1
		self.fd.flush()

	def threecol(self, filespec, tcdata):
		d = [ '%d %d %s' % (int(round(t0*self.scale)),
					int(round(te*self.scale)),
					lbl) 
			for (t0, te, lbl) in tcdata
			]
		self.chunk(filespec, d)

	def close(self):
		self.fd.writelines('\n')
		self.fd = None	# Normally, this will close the file.

	def __del__(self):
		if self.fd is not None:
			self.close()


if __name__ == '__main__':
	import sys
	THREECOL = False
	DATAPATH = None
	arglist = sys.argv[1:]
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '-threecol':
			THREECOL = True
		elif arg == '-datapath':
			DATAPATH = arglist.pop(0)
		else:
			die.die('Unrecognized argument: %s' % arg)
	for tmp in readiter(arglist[0], datapath=DATAPATH,
				threecol=THREECOL, findfile=(DATAPATH is not None)
				):
		print '[', tmp['filespec'], tmp.get('d', ''), tmp.get('f', ''), ']'
		for tmps in tmp['symbols']:
			if THREECOL:
				print tmps[0], tmps[1], tmps[2]
			else:
				print tmps
