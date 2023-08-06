"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.
"""

from __future__ import with_statement
import sys
import random
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

	def update(self, x, nsteps):
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
				self.last_resetid = tmp
				self.erg = 0.0
			else:
				self.erg += x.ergodic() * nsteps


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


	def reset_loops(self, maxloops=-1):
		self.maxloops = maxloops


	def run_to_change(self, ncw=1, acceptable_step=None, update_T=False):
		"""Run the X{Markov Chain Monte-Carlo} until it finds
		an acceptable step.

		@param ncw: How many steps should be accepted before it stops?
		@type ncw: int
		@param acceptable_step: A function that decides what steps are acceptable and what are not.
			This is passed to the MCMC stepper, L{mcmc.BootStepper}.
		@type acceptable_step: function(float) -> bool, often L{mcmc.T_acceptor} or L{step_acceptor}
		@param update_T: Obsolete.   Must be False.
		@type update_T: boolean.
		@raise TooManyLoops: if it takes a long time before enough steps are accepted.
		"""
		assert not update_T, "Obsolete!"
		if acceptable_step is not None:
			old_acceptable = self.x.acceptable
			self.x.acceptable = acceptable_step
		else:
			old_acceptable = None
		n = 0
		self.communicate_hook("RTT:%d" % ncw)
		try:
			while n < ncw:
				n += self.x.step()
				self.logger.add(self.x, self.iter)
				if self.maxloops > 0:
					self.maxloops -= 1
				if self.maxloops == 0:
					raise TooManyLoops, "run_to_change"
				self.iter += 1
		finally:
			if old_acceptable is not None:
				self.x.acceptable_step = old_acceptable
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


	def _nc_get_hook(self, nc):
		return nc.get()


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
		ISSMAX = 20
		self.join('rte before loop')
		if T is not None:
			acceptable_step = mcmc.T_acceptor(T)
		else:
			acceptable_step = None
		ss = self.x.set_sort_strategy(self.x.SSNEVER)
		nc = _accum_erg()
		try:
			iss = 1
			while True:
				ncg = self._nc_get_hook(nc)
				if ncg >= ncw:
					break
				elif ncg < 0.5*ncw and iss<ISSMAX:
					iss += 1
				# print 'ncg=', ncg, '/', ncw, 'iss=', iss
				self.run_to_change(ncw=iss, acceptable_step=acceptable_step)
				nc.update(self.x, iss)
		finally:
			self.x.set_sort_strategy(ss)	# Return to previous sortstrategy.
		# There will be trouble if you get an exception caused by maxloops.
		# There is yet no way to synchronize all MPI threads.
		self.join('rte after loop')
		return self.x.current()




	def _not_at_bottom(self, xchanged, nchg, es, dotchanged, ndot):
		return (Num.sometrue(Num.less(xchanged,nchg))
					or es<1.0 or dotchanged<ndot
					or self.x.acceptable.T()>1.5
				)


	def run_to_bottom(self, ns=3, acceptable_step=None, update_T=False):
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
			originally gave it.   OBSOLETE.
			Use C{acceptable_step} instead.
		@type update_T: boolean.
		"""
		m = self.x.np
		if update_T and acceptable_step is None:	#Backwards compatibility
			acceptable_step = step_acceptor(n=m, T0=10.0, T=1.0, ooze=0.5)
		else:
			acceptable_step = self.x.acceptable
		nchg = int(round(ns * m**0.25))
		ndot = int(round((2*ns)**0.5))
		for i in range(2+m//2):
			self.run_to_change(5, acceptable_step=acceptable_step)	# get it warmed up.
		before = self.run_to_change(ns, acceptable_step=acceptable_step)
		mid = self.run_to_change(ns, acceptable_step=acceptable_step)
		es = 0.0
		lock = Thr.allocate_lock()
		xchanged = Num.zeros(m, Num.Int)
		dotchanged = 0
		last_resetid = self.x.reset_id()
		while self._not_at_bottom(xchanged, nchg, es, dotchanged, ndot):
			try:
				after = self.run_to_change(ns, acceptable_step=acceptable_step)
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
				self.note('run_to_bottom: Reset: T=%g' % acceptable_step.T(), 1)
			else:
				lock.release()
				self.note('run_to_bottom: T=%g' % acceptable_step.T(), 3)

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



class step_acceptor(object):
	def __init__(self, n, T0, T, ooze):
		ooze = float(ooze)
		assert 0.0 <= ooze < 1.0
		T = float(T)
		assert T > 0 and T0>0
		assert n > 0
		self._T = T
		self.ooze = ooze
		self.E = [random.expovariate(1.0)*T0 for i in range(n+1)]


	def T(self):
		sum = 0.0
		for e in self.E:
			sum += e
		return sum/len(self.E)


	def __call__(self, delta):
		# print 'delta=', delta, "E=", self.E
		n = len(self.E)
		i = random.randrange(n)
		ok = delta > -self.E[i]
		if not ok:
			j = random.randrange(n)
			if j != i:
				sum = self.E[i] + self.E[j]
				f = random.random()
				self.E[i] = f*sum
				self.E[j] = sum - self.E[i]
				# print 'Not OK E->', self.E
			return False
		self.E[i] = (delta + self.E[i])*self.ooze + self._T*(1.0-self.ooze)
		# print 'OK: updating E[%d] to %g' % (i, self.E[i])
		return True

	def __repr__(self):
		return '<step_acceptor(T=%g o=%g) %s>' % (self._T, self.ooze, str(self.E))



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
	# mcmc.Debug = 3
	# Debug = 3
	x = mcmc.bootstepper(test_logp, Num.array([0.0,2.0]),
				Num.array([[1.0,0],[0,2.0]]))
	thr = stepper(x)
	nsteps = thr.run_to_bottom(acceptable_step=step_acceptor(x.np, 5.0, 1.0, 0.5))
	print '#nsteps', nsteps
	assert nsteps < 300
	for i in range(2):
		print 'RTC'
		thr.run_to_change(2)
		print 'RTE'
		thr.run_to_ergodic(1.0)
		print 'DONE'
	thr.close()




if __name__ == '__main__':
	test()
