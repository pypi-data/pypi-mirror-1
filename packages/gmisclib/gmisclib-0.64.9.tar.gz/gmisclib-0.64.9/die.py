"""This class handles error logging.
Duplicate messages are lumped together.
It will remember notes that will be printed
if there is a later error/warning message.
The notes are printed in chronological order.
"""

import sys
import os
import traceback

__version__ = "$Revision: 1.21 $"

debug = True	# Set to False to disable dbg() messages.
nocompress = False

_name = os.path.basename(sys.argv[0])
_stderr = sys.stderr
_stdout = sys.stdout


class counter:
	def __init__(self):
		self.reps = 0
		self.last = None
		self.sequence = 0
		self.memory = {}
		self.stderr = _stderr
		self.stdout = _stdout
		assert self.stderr is not None
		assert self.stdout is not None

	def incoming(self, id, name, s):
		t = (id, name, s)
		# print "# t=", t, "last=", self.last
		if nocompress or t != self.last:
			self.stderr.flush()
			self.stdout.flush()
			self.showreps()
			self.dumpmem()
			self.stderr.write('%s: %s: %s\n' % (id, name, s))
			self.stderr.flush()
			self.last = t
		else:
			self.clearmem()
			self.reps += 1
		self.stderr = _stderr
		self.stdout = _stdout
		assert self.stderr is not None
		assert self.stdout is not None

	def showreps(self):
		if self.last is not None and self.reps>1:
			self.stderr.write('%s: last message repeated %d times.\n'
						% (self.last[0], self.reps))
			self.last = None
			self.reps = 1

	def __del__(self):
		self.showreps()

	def clearmem(self):
		self.memory = {}
		self.sequence = 0

	def dumpmem(self):
		tmp = [(sqn, k, val) for (k, (sqn,val)) in self.memory.items()]
		tmp.sort()
		for (sqn,k,val) in tmp:
			self.stderr.write('#NOTE: %s = %s\n' % (str(k), str(val)))
		self.clearmem()

	def memorize(self, key, value):
		self.memory[key] = (self.sequence, value)
		self.sequence += 1

_q = counter()

def die(s):
	"""Output a fatal error message and terminate."""
	e = 'ERR: %s: %s' % (_name, s)
	exit(1, e)


def warn(s):
	"""Output a non-fatal warning."""
	global _q
	_q.incoming('#WARN', _name, s)


def info(s):
	"""Output useful information."""
	global _q
	_q.incoming('#INFO', _name, s)


def catch(extext=None):
	"""Call this inside an except statement.
	It will report the exception and any other information it has."""
	etype, value, tback = sys.exc_info()
	if extext is None:
		extext = "die.catch: exception caught.\n"
	_stderr.flush()
	_stdout.flush()
	_q.showreps()
	_q.dumpmem()
	traceback.print_exception(etype, value, tback)
	etype = None
	value = None
	tback = None
	_stderr.flush()
	_stdout.flush()
	

def catchexit(extext=None, n=1, text=None):
	"""Call this inside an except statement.  It will report
	all information and then exit."""
	catch(extext)
	exit(n, text=text)

def dbg(s):
	"""Output debugging information, if debug is nonzero."""
	if debug:
		global _q
		_q.incoming('#DBG', _name, s)

def exit(n, text=None):
	"""Exit, after dumping accumulated messages."""
	global _q
	_stderr.flush()
	_stdout.flush()
	_q.showreps()
	_q.dumpmem()
	_stderr.flush()
	if text is not None:
		_stdout.write('%s\n' % text)
		_stdout.flush()
	if text is not None:
		_stderr.write('%s\n' % text)
		_stderr.flush()
	sys.exit(n)


def note(key, value):
	"""Memorize a note, which will be output along with the next error/warning/info message."""
	global _q
	_q.memorize(key, value)


def get(key):
	try:
		return _q.memory.get(key, None)[1]
	except KeyError:
		pass
	return None

if __name__ == '__main__':
	debug = 1
	info("You should see a debug message next.")
	dbg("This is the debug message.")
	debug = 0
	note("gleep", "oldest note")
	note("foo", "bar")
	note("foo", "fleep")
	note("foo", "foo")
	note("farf", "newest note")
	info("You should not see a debug message next.")
	dbg("This is the debug message you shouldn't see.")
	warn("This is a warning.")
	warn("This is a warning.")
	warn("This is a warning.")
	info("It should have been repeated three times.")
	die("This is the end.")
