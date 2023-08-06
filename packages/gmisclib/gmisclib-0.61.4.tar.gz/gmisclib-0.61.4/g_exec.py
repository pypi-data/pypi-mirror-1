"""Run a *nix command and capture the result.
This module is thread-safe."""

import re
import g_pipe

comment = re.compile("\\s*#");

class ExecError(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


def getiter_raw(s, argv, input=None, perline=None, debug=False):
	"""Read a list of lines from a process.
	Input is a sequence or iterator containing strings to feed
	to the process on startup, before the first output is read.
	Perline is a sequence/iterator of strings to feed in, one at a time,
	as the process is producing data.
	Note that if input or perline is badly chosen, one can
	produce a locked loop of pipes.
	"""

	if argv is None:
		argv = [s]
	elif s is None:
		s = argv[0]

	if debug:
		print '#OPENING', s, argv
	wpipe, rpipe = g_pipe.popen2(s, argv)

	if wpipe is None or rpipe is None:
		raise ExecError('Cannot spawn pipe for {%s}' % s, *argv)
	if input is not None:
		if debug:
			for t in input:
				print '#WRITING <%s>' % t
				wpipe.write(t)
		else:
			for t in input:
				wpipe.write(t)

	if perline is None:
		wpipe.close()
		wpipe = None
	else:
		wpipe.flush()
		perline = perline.__iter__()

	while True:
		if wpipe is not None:
			try:
				wpipe.write(perline.next())
				wpipe.flush()
			except StopIteration:
				wpipe.close()
				wpipe = None
				pass
		line = rpipe.readline();
		if not line:
			break
		if debug:
			print '#LINE:', line.rstrip('\n')
		yield line

	if wpipe is not None:
		wpipe.close()
		if perline is not None:
			raise ExecError("Unused input: program {%s} terminated before perline ran out of data" % s,
					*argv)
	sts = rpipe.close()
	# if sts is None:
		# sts = 0
	if sts != 0 :
		raise ExecError('spawned command fails with %d from {%s}' % (sts, s), *argv)


def getiter(s, argv, input=None, perline=None, debug=False):
	"""Read a list of lines from a process, after
	dropping junk like comments (#).
	Returns a trouble indication if the process returns
	'ERR:'
	Input is a sequence or iterator containing strings to feed
	to the process on startup, before the first output is read.
	Perline is a sequence/iterator of strings to feed in, one at a time,
	as the process is producing data.
	Note that if input or perline is badly chosen, one can
	produce a locked loop of pipes.
	"""

	for line in getiter_raw(s, argv, input=input, perline=perline, debug=debug):
		if line.startswith('#'):
			continue;
		line = line.rstrip()
		if line.startswith('ERR:'):
			raise ExecError('%s from {%s}' % (line, s), *argv)
		cs = comment.search(line)
		if cs is not None:
			line = cs.string[:cs.start()]
		yield line


def get(s, argv=None, input=None, perline=None, debug=False):
	"""Read a single line from a process, after
	dropping junk like comments (#).
	Raises an exception if the process returns
	'ERR:' or produces no output.
	"""
	try:
		return getiter(s, argv, input, perline=perline, debug=debug).next()
	except StopIteration:
		raise ExecError('no output fron {%s}' % s, *argv)


def get_raw(s, argv=None, input=None, perline=False, debug=False):
	"""Read a single line from a process.
	Returns None if there is no output.
	"""
	try:
		return getiter(s, argv, input, perline=perline, debug=debug).next()
	except StopIteration:
		return None

def getlast(s, argv=None, input=None, perline=False, debug=False):
	"""Read a single line from a process, after
	dropping junk like comments (#).
	Raises an exception if the process returns
	'ERR:' or produces no output.
	"""
	ok = False
	for q in getiter(s, argv, input, perline=perline, debug=debug):
		ok = True
	if ok:
		return q
	else:
		raise ExecError('no output fron {%s}' % s, *argv)

def getall(s, argv, input=None, perline=None, debug=False):
	return [ q for q in getiter(s, argv, input=input,
					perline=perline, debug=debug
				)
		]



def test():
	inp = ['once\n', 'upon\n', 'a\n', 'time.\n']
	die.note('inp', inp)
	oup = getall(None, ['cat'], input=inp)
	die.note('oup', oup)
	if inp != ["%s\n" % q for q in oup]:
		die.die('whoops: bad cat')
	

if __name__ == '__main__':
	import die
	test()
	test()
	test()
	print 'OK'
