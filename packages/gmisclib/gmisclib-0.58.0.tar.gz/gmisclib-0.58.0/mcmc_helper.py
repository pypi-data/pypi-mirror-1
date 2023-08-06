"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.
"""

from __future__ import with_statement
import sys
import thread as Thr
from gmisclib import Num
from gmisclib import g_implements
from gmisclib import mcmc

Debug = 0

class TooManyLoops(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


class warnevery(object):
	def __init__(self, interval):
		self.c = 0
		self.interval = interval
		self.lwc = 0
	
	def inc(self, incr=1):
		self.c += incr
		if self.c > self.lwc + self.interval:
			self.lwc = self.c
			return 1
		return 0

	def count(self):
		return self.c


class _counter(object):
	def __init__(self):
		self.lock = Thr.allocate_lock()
		self.count = 0

	def update(self, accepted):
		with self.lock:
			self.count += accepted

	def get(self):
		with self.lock:
			tmp = self.count
		return tmp



class _accum_erg(object):
	def __init__(self):
		self.lock = Thr.allocate_lock()
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
		with self.lock:
			tmp = x.reset_id()
			if tmp != self.last_resetid:
				self.erg = 0.0
				self.last_resetid = tmp
			else:
				self.erg += x.ergodic()


	def get(self):
		with self.lock:
			tmp = self.erg
		return tmp


class logger_template(object):
	def add(self, stepperInstance, iter):
		pass

	def close(self):
		pass




class stepper(object):
	def __init__(self, x, maxloops=-1, logger=None):
		self.logger = None	# This sets things up for close()
		self.iter = 0
		self.maxloops = maxloops
		g_implements.check(x, mcmc.stepper)
		self.x = x
		if logger is None:
			self.logger = logger_template()
		else:
			g_implements.check(logger, logger_template)
			self.logger = logger
		self.OOZE = 0.9


	def reset_loops(self, maxloops=-1):
		self.maxloops = maxloops


	def run_to_change(self, ncw=1, update_T=False):
		"""Run the X{Markov Chain Monte-Carlo} until it finds
		an acceptable step.

		@param update_T: Permission to fiddle with the simulated
			annealing temperature.   If C{update_T} is False,
			C{self.x.T} is left with whatever value you
			originally gave it.
		@type update_T: boolean.
		"""
		assert 0 <= self.OOZE < 1.0
		ooze = self.OOZE**(1.0/self.x.np)
		T = self.x.T
		n = 0
		self.communicate_hook("RTT:%d:%s" % (ncw, update_T))
		while n < ncw:
			if update_T:
				pre_logp = self.x.current().logp_nocompute()
			acc = self.x.step()
			if acc and update_T:
				logp = self.x.current().logp_nocompute()
				T = (T+0.25*(logp-pre_logp))*ooze
				self.x.T = max(1.0, T)
				self.note('Updating T to %.1f because %.1f -> %.1f' % (self.x.T, pre_logp, logp), 2)
			n += acc
			self.logger.add(self.x, self.iter)
			if self.maxloops > 0:
				self.maxloops -= 1
			if self.maxloops == 0:
				raise TooManyLoops, "run_to_change"
			self.iter += 1
		self.join('rtc end')
		return self.x.current()


	def communicate_hook(self, id):
		return


	def close(self):
		"""After calling close(), it is no longer legal
		to call run_to_change(), run_to_ergodic(), or
		run_to_bottom().    Logging is shut down, but the
		contents of the stepper are still available for
		inspection.
		"""
		if self.logger is not None:
			self.logger.close()
			self.logger = None


	# def __del__(self):
		# self.close()


	def _not_yet_ergodic(self, nc, ncw):
		return nc.get() < ncw


	def run_to_ergodic(self, ncw=1, T=1.0):
		"""Run the stepper until it has explored all of parameter space
		C{ncw} times (as best as we can estimate).   Note that this
		is a pretty careful routine.   If the stepper finds a better
		region of parameter space so that log(P) improves part way
		through the process, the routine will reset itself and begin
		again.

		NOTE: this sets C{T} and C{sortstrategy} for the L{stepper<mcmc.BootStepper>}.

		@param ncw: how many times (or what fraction) of an ergodic
			exploration to make.
		@type ncw: int.
		@param T: temperature at which to run the Monte-Carlo process.
			This is normally 1.0.   If it is C{None}, then the
			current temperature is not modified.
		@type T: C{float} or C{None}.
		@return: a L{position<mcmc.position_base>} at the end of the process.
		"""
		self.join('rte before loop')
		if T is not None:
			self.x.T = T
		ss = self.x.set_sort_strategy(self.x.SSNEVER)
		nc = _accum_erg()
		while self._not_yet_ergodic(nc, ncw):
			# self.join('rte loop top')
			self.communicate_hook("rte:%s:%g" % (ncw, T))
			for i in range(4):
				self.x.step()
				self.logger.add(self.x, self.iter)
				nc.update(self.x)
				self.iter += 1
				if self.maxloops > 0:
					self.maxloops -= 1
				if self.maxloops == 0:
					raise TooManyLoops, ("run_to_ergodic", nc.get(), ncw)
		self.x.set_sort_strategy(ss)	# Return to previous sortstrategy.
		self.join('rte after loop')
		return self.x.current()




	def _not_at_bottom(self, xchanged, nchg, es, dotchanged, ndot, update_T):
		return (Num.sometrue(Num.less(xchanged,nchg))
					or es<1.0 or dotchanged<ndot
					or (update_T and self.x.T>1.5)
				)


	def run_to_bottom(self, ns=3, update_T=True):
		"""Run the X{Markov Chain Monte-Carlo} until it converges
		near a minimum.

		@param ns: This controls how carefully if checks that
			it has really found a minimum.   Large values
			will take longer but will assure more accurate
			convergence.
		@type ns: L{int}
		@param update_T: Permission to fiddle with the simulated
			annealing temperature.   If C{update_T} is False,
			C{self.x.T} is left with whatever value you
			originally gave it.
		@type update_T: boolean.
		"""
		m = self.x.np
		nchg = int(round(ns * m**0.25))
		ndot = int(round((2*ns)**0.5))
		for i in range(2+m//2):
			self.run_to_change(5, update_T=update_T)	# get it warmed up.
		before = self.run_to_change(ns, update_T=update_T)
		mid = self.run_to_change(ns, update_T=update_T)
		es = 0.0
		lock = Thr.allocate_lock()
		xchanged = Num.zeros(m, Num.Int)
		dotchanged = 0
		last_resetid = self.x.reset_id()
		while self._not_at_bottom(xchanged, nchg, es, dotchanged, ndot, update_T):
			try:
				after = self.run_to_change(ns, update_T=update_T)
			except TooManyLoops, x:
				raise TooManyLoops, ('run_to_bottom: s' % x, self.iter, es, dotchanged, m,
							Num.sum(Num.less(xchanged, nchg)),
							self.x.current().prms()
							)
			# We keep track of direction reversals to see when
			# we reach the bottom.
			Num.add(xchanged,
				Num.less( (after.vec()-mid.vec())
						* (mid.vec()-before.vec()), 0.0),
				xchanged)

			dotchanged += Num.dot(after.vec()-mid.vec(),
						mid.vec()-before.vec()) < 0.0

			es += self.x.ergodic() * ns**0.5

			# print 'LA'
			lock.acquire()
			if self.x.reset_id() != last_resetid:
				# A new maximum: we are probably
				# not stable.  Likely, we are still in the
				# improvement phase.
				last_resetid = self.x.reset_id()
				lock.release()
				es = 0.0
				xchanged[:] = 0
				dotchanged = 0
			else:
				lock.release()

			before = mid
			mid = after
		self.join('rtb after loop')
		return self.iter


	def join(self, id):
		return

	def note(self, s, lvl):
		if Debug >= lvl:
			print s
			sys.stdout.flush()


def is_root():
	"""This is a stub for compatibility with MPI code."""
	return True

def size():
	"""This is a stub for compatibility with MPI code."""
	return 1


def test():
	def test_logp(x, c):
		# print '#', x[0], x[1]
		return -(x[0]-x[1]**2)**2 + 0.001*x[1]**2
	x = mcmc.bootstepper(test_logp, Num.array([0.0,2.0]),
				Num.array([[1.0,0],[0,2.0]]))
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
