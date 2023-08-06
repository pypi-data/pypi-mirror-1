"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.

When run in parallel, each processor does its thing more-or-less
independently.   However, every few steps, they exchange notes on
their current progress.   If one finds an improved vertex, it will be
passed on to other processors via MPI.
"""

import sys
import mpi		# This uses pyMPI
import random
from gmisclib import die
from gmisclib import Num
from gmisclib import gpkmisc
from gmisclib import mcmc
from gmisclib import mcmc_helper as MCH
Debug = 0
from gmisclib.mcmc_helper import TooManyLoops, warnevery, test, logger_template


class _counter(object):
	def __init__(self):
		self.count = 0

	def update(self, accepted):
		self.count += accepted

	def get(self):
		return self.count



class _accum_erg(object):
	def __init__(self):
		self.erg = 0.0
		self.last_resetid = -1

	def update(self, x):
		"""Increment an accumulator, but reset it to
		zero if the underlying stepper has called reset().
		The increment is by the ergodicity estimate, so
		C{self.erg} should approximate how many times the
		MCMC process had wandered across the probability
		distribution.
		"""
		tmp = x.reset_id()
		if tmp != self.last_resetid:
			self.erg = 0.0
			self.last_resetid = tmp
		else:
			self.erg += x.ergodic()


	def get(self):
		return self.erg


class comm_offset(object):
	"""This just provides a string of more-or-less random numbers that is identical on
	each processor.  It's used to decide which processor communicates with which.
	"""
	def __init__(self, size):
		self.n = size
		self.i = 1
		self.a = 1
		for p in gpkmisc.primes():
			if p >= size:
				break
			if p>1 and gpkmisc.gcd(p, size)==1:
				self.a = p
				break
		self.m = 197
		for p in gpkmisc.primes():
			if p >= size:
				break
			if p>5 and gpkmisc.gcd(p, size)==1 and gpkmisc.gcd(p, self.a)==1 and gpkmisc.gcd(p*self.a, size)==1:
				self.m = p
				break

	def __call__(self):
		assert self.n > 0
		while True:
			self.i = (self.i*self.m + self.a) % self.n
			if self.i != 0:
				break
		return self.i


class stepper(MCH.stepper):
	def __init__(self, x, maxloops=-1, logger=None):
		die.info('# mpi stepper rank=%d size=%d' % (mpi.rank, mpi.size))
		assert maxloops == -1
		self.maxloops = -1
		if mpi.size > 1:
			self.co = comm_offset(mpi.size)
		else:
			self.co = None
		MCH.stepper.__init__(self, x, maxloops, logger)


	def reset_loops(self, maxloops=-1):
		assert maxloops == -1
		self.maxloops = -1


	def communicate_hook(self):
		self.note('chook iter=%d' % self.iter, 4)
		if mpi.size > 1:
			self.note('chook active iter=%d' % self.iter, 3)
			handle = mpi.irecv(tag=self.MPIID)
			c = self.x.current()
			v = c.vec()
			lp = c.logp()
			co = self.co()
			mpi.send((v, lp, co), (mpi.rank+co)%mpi.size, tag=self.MPIID)
			handle.wait()
			nv, nlp, nco = handle.message
			assert nco == co

			if nlp > lp - self.x.T*random.expovariate(1.0):
				q = self.x._set_current(c.new(nv-v, logp=nlp))
				self.note('communicate succeeded: %s' % q, 1)
			else:
				self.note('communicate not accepted %g vs %g' % (nlp, lp), 1)
				self.x._set_current(self.x.current())
			sys.stdout.flush()


	MPIID = 1241

	# def _not_enough_changes(self, n, ncw):
		# mytmp = n < ncw
		# self.note('_nyc pre')
		# ntrue = mpi.allreduce(int(mytmp), mpi.SUM)
		# self.note('_nyc post')
		# return ntrue*3 >= mpi.size


	def _not_yet_ergodic(self, nc, ncw):
		mytmp = nc.get() < ncw
		self.note('_nye pre', 5)
		ntrue = mpi.allreduce(int(mytmp), mpi.SUM)
		self.note('_nye post', 5)
		return ntrue*2 >= mpi.size


	def _not_at_bottom(self, xchanged, nchg, es, dotchanged, ndot, update_T):
		mytmp = (Num.sometrue(Num.less(xchanged,nchg))
					or es<1.0 or dotchanged<ndot
					or (update_T and self.x.T>1.5)
				)
		self.note('_nab pre', 5)
		ntrue = mpi.allreduce(int(mytmp), mpi.SUM)
		self.note('_nab post', 5)
		return ntrue*4 >= mpi.size


	def join(self, id):
		self.note('pre join %s' % id, 5)
		rootid = mpi.bcast(id)
		assert rootid == id
		self.note('post join %s' % id, 5)

	def note(self, s, lvl):
		if Debug >= lvl:
			sys.stderr.writelines('# %s, rank=%d\n' % (s, mpi.rank))
			sys.stderr.flush()


def precompute_logp(lop):
	"""Does a parallel evaluation of logp for all items in lop.
	"""
	nper = len(lop)//mpi.size
	r = mpi.rank
	mychunk = lop[r*nper:(r+1)*nper]
	for p in mychunk:
		q = p.logp()
		print 'logp=', q, 'for rank', r
	for r in range(mpi.size):
		nc = mpi.bcast(mychunk, r)
		lop[r*nper:(r+1)*nper] = nc
	mpi.barrier()


def is_root():
	return mpi.rank == 0

def size():
	return mpi.size


def test():
	def test_logp(x, c):
		# print '#', x[0], x[1]
		return -(x[0]-x[1]**2)**2 + 0.001*x[1]**2
	x = mcmc.bootstepper(test_logp, Num.array([0.0,2.0]),
				Num.array([[1.0,0],[0,2.0]]))
	print 'rank=', mpi.rank
	thr = stepper(x)
	# nsteps = thr.run_to_bottom(x)
	# print '#nsteps', nsteps
	# assert nsteps < 100
	for i in range(2):
		print 'RTC'
		thr.run_to_change(2)
		print 'RTE'
		thr.run_to_ergodic(1.0)
		print 'DONE'
	thr.close()


if __name__ == '__main__':
	test()
