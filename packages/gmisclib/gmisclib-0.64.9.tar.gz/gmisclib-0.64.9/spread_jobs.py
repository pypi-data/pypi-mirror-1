#! python

from __future__ import with_statement

import re
import sys
import time
import Queue
import cPickle as CP
import threading
import subprocess
import StringIO

from gmisclib import die
from gmisclib import gpkmisc


class notComputed(object):
	"""Just a marker for values that haven't been computed."""
	pass


class LockedList(object):
	def __init__(self):
		self.lock = threading.Lock()
		self.data = []


	def put(self, i, x):
		with self.lock:
			if len(self.data) == i:
				self.data.append(x)
			elif len(self.data) > i:
				assert self.data[i] is notComputed
				self.data[i] = x
			else:
				while len(self.data) < i:
					# "self" is used as a marker for entries that
					# have not been set.   get() makes sure they
					# are all gone before returning an array.
					self.data.append(notComputed)
				self.data.append(x)
	
	def __len__(self):
		with self.lock:
			tmp = len(self.data)
		return tmp


	def get(self):
		tmp = []
		with self.lock:
			for x in self.data:
				if isinstance(x, raiseException):
					x.raise_me()
				assert x is not notComputed
				tmp.append(x)
		return tmp



class NoResponse(RuntimeError):
	def __init__(self, *s):
		RuntimeError.__init__(self, *s)


class RemoteException(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


class raiseException(object):
	def __init__(self, *s):
		self.args = s
		self.index = ""
		self.comment = ''

	def raise_me(self):
		raise RemoteException(*(self.args + (self.index,self.comment)) )




class ThreadJob(threading.Thread):
	def __init__(self, iqueue, olist, args, stdin, solock, verbose=False):
		threading.Thread.__init__(self)
		self.timing = []
		self.iqueue = iqueue
		self.olist = olist
		self.p = None
		if verbose:
			die.info("Spawning process: %s" % str(args))
		self.spawn_process(args)
		self.solock = solock
		for x in stdin:
			self.send(x)
	

	def run(self):
		# sys.stderr.write('run-starting\n')
		while True:
			# sys.stderr.write('run-loop\n')
			i, todo = self.iqueue.get()
			if i is None:
				self.iqueue.task_done()
				break
			# sys.stderr.write('run-loop %s %s\n' % (i, todo))
			t0 = time.time()
			try:
				self.send(todo)
			except IOError, x:
				die.warn("IO Error on send %d to worker: %s" % (i, str(x)))
				self.iqueue.put((i, todo))
				self.iqueue.task_done()
				break
			# sys.stderr.write('run-sent\n')
			q, so, se = self.get()
			t2 = time.time()
			self.timing.append(t2-t0)
			# sys.stderr.write('run-got %s %s %s\n' % (q, so, se))
			self.olist.put(i, q)
			# sys.stderr.write('run-completed\n')
			with self.solock:
				if so:
					sys.stdout.writelines('#slot so%d ------\n' % i)
					sys.stdout.writelines(so)
					sys.stdout.flush()
				if se:
					sys.stderr.writelines('#slot se%d ------\n' % i)
					sys.stderr.writelines(se)
					sys.stderr.flush()
			# sys.stderr.write('run-bottom\n')
			self.iqueue.task_done()
			if isinstance(q, raiseException):
				die.info("Remote Exception info: %s" % str(q.args))
				die.warn("Exception from remote job (index=%d): %s" % (i, str(q)))
				q.index = "index=%d" % i
				q.comment = "stderr=%s" % gpkmisc.truncate('/'.join(se), 40)
				# Eat all remaining jobs
				while True:
					i, todo = self.iqueue.get()
					self.iqueue.task_done()
					if i is None:
						break
					self.olist.put(i, notComputed)


	def spawn_process(self, args):
		self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					close_fds=True
					)

	def send(self, todo):
		CP.dump(todo, self.p.stdin)
		self.p.stdin.flush()
		# sys.stdout.write('send - completed.\n')


	def get(self):
		while True:
			try:
				q, so, se = CP.load(self.p.stdout)
				return (q, so, se)
			except CP.UnpicklingError, y:
				die.warn("spread_load: Junk response: %s" % str(y))
				die.info("Remainder: %s" % self.p.readline())
				continue
		return None

	def close(self):
		self.p.stdin.close()
		self.p.wait()
		self.p.stdout.close()


def main(todo, list_of_args, stdin=None, verbose=False, timing_callback=None):
	"""Pass a bunch of work to other processes.
	@param stdin: a list of stuff to send to the other processes before the computation is
		properly commenced.
	@type stdin: list(whatever)
	@param todo: a list of work to do
	@type todo: list(whatever)
	@param list_of_args:
	@type list_of_args:  list(list(str))
	@rtype: list(whatever)
	@return: a list of the results produced by the other processes.
		Items in the returned list correspond to items in the todo list.
	"""
	# sys.stderr.write('main starting\n')
	iqueue = Queue.Queue()
	olist = LockedList()
	solock = threading.Lock()
	if stdin is None:
		stdin = []
	ths = []
	for args in list_of_args:
		t = ThreadJob(iqueue, olist, args, stdin, solock, verbose=verbose)
		# t.setDaemon(True)
		t.start()
		ths.append(t)
	# sys.stderr.write('all threads started\n')
	for (i, job) in enumerate(todo):
		# sys.stderr.write('put %d %s\n' % (i, job))
		iqueue.put( (i,job) )
	# sys.stderr.write('all work queued\n')
	for args in list_of_args:
		iqueue.put( (None,None) )
	iqueue.join()
	# sys.stderr.write('all threads joined\n')
	timing = []
	for t in ths:
		# sys.stderr.write('close %s\n' % t)
		timing.extend(t.timing)
		t.close()
	# sys.stderr.write('main done\n')
	assert len(olist) == len(todo)
	if timing_callback is not None:
		timing_callback(timing)
	return olist.get()



def test_worker():
	# sys.stderr.write('test_worker starting\n')
	while True:
		# sys.stderr.write('test_worker loop\n')
		try:
			control = CP.load(sys.stdin)
		except EOFError:
			# sys.stderr.write('test_worker break')
			break
		# sys.stderr.write('test_worker dump\n')
		CP.dump((control, ['stdout\n'], ['stderr\n']), sys.stdout, CP.HIGHEST_PROTOCOL)
		sys.stdout.flush()

def test():
	x = ['a', 'b', 'c', 'd', 'e']
	args = ['python', sys.argv[0], 'worker']
	y = main(x, [args]*3 )
	assert x == y



class unpickled_pseudofile(StringIO.StringIO):
	"""For testing.
	"""

	def __init__(self):
		StringIO.StringIO.__init__(self)

	def close(self):
		self.seek(0, 0)
		while True:
			try:
				d, so, se = CP.load(self)
			except EOFError:
				break
			sys.stdout.write('STDOUT:\n')
			sys.stdout.writelines(so)
			sys.stdout.write('STDERR:\n')
			sys.stdout.writelines(se)
			sys.stdout.write('d=%s\n' % str(d))
			sys.stdout.flush()


def one_shot_test(input):
	stdin = StringIO.StringIO()
	CP.dump(input, stdin)
	stdin.flush()
	stdin.seek(0, 0)
	stdout = unpickled_pseudofile()
	return (stdin, stdout)



def replace(list_of_lists, *fr):
	assert isinstance(list_of_lists, list)
	frc = []
	while fr:
		frc.append( (re.compile(fr[0]), fr[1]) )
		fr = fr[2:]
	o = []
	for l in list_of_lists:
		assert isinstance(l, (tuple, list)), "List of lists contains %s within %s" % (repr(l), list_of_lists)
		tmp = []
		for t in l:
			for (find, repl) in frc:
				assert isinstance(t, str), "whoops! t=%s" % str(t)
				t = find.sub(repl, t)
			tmp.append(t)
		o.append(tmp)
	return o


def Replace(list_of_lists, pat, length, replacement):
	assert isinstance(replacement, list)
	assert length > 0
	cpat = re.compile(pat)
	o = []
	for l in list_of_lists:
		assert isinstance(l, (tuple, list)), "List of lists contains %s within %s" % (repr(l), list_of_lists)
		tmp = list(l)
		while tmp:
			found = None
			print 'X=', tmp
			for (i, t) in enumerate(tmp):
				if cpat.match(t):
					print 'MATCH %s to %s' % (t, pat)
					found = i
					break
			if found is not None:
				print 'REPLACE %s -> %s' % (str(tmp[i:i+length]), str(replacement))
				tmp[i:i+length] = list(replacement)
			else:
				break
		o.append(tmp)
	return o


def append(list_of_lists, *a):
	o = []
	for l in list_of_lists:
		tmp = tuple(l) + a
		o.append(tmp)
	return o


if __name__ == '__main__':
	if len(sys.argv)==2 and sys.argv[1] == 'worker':
		test_worker()
	else:
		test()
