"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.
"""

import thread as Thr
import Num
import g_implements
import mcmc

NW = 20
NWE = 300
ERGL = 0.10
NSF = 20
EWC = 100


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
		self.lock.acquire()
		self.count += accepted
		self.lock.release()

	def get(self):
		self.lock.acquire()
		tmp = self.count
		self.lock.release()
		return tmp



class _accum_erg(object):
	def __init__(self):
		self.lock = Thr.allocate_lock()
		self.erg = 0.0
		self.last_resetid = -1

	def update(self, x):
		self.lock.acquire()
		tmp = x.reset_id()
		if tmp != self.last_resetid:
			self.erg = 0.0
			self.last_resetid = tmp
		else:
			self.erg += x.ergodic()
		self.lock.release()


	def get(self):
		self.lock.acquire()
		tmp = self.erg
		self.lock.release()
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


	def run_to_change(self, ncw=1, update_T=False):
		n = 0
		while n < ncw:
			if update_T:
				pre_logp = self.x.current().logp_nocompute()
			else:
				self.x.T = 1.0
			acc = self.x.step()
			if acc and update_T:
				logp = self.x.current().logp_nocompute()
				self.x.T = max(1.0, self.x.T*0.90 + 0.4*(logp-pre_logp))
			n += acc
			self.logger.add(self.x, self.iter)
			self.maxloops -= 1
			if self.maxloops == 0:
				raise TooManyLoops, "run_to_change"
			self.iter += 1
		return self.x.current()


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


	def __del__(self):
		self.close()


	def run_to_ergodic(self, ncw=1):
		"""Run the stepper until it has explored all of parameter space
		C{ncw} times (as best as we can estimate).   Note that this
		is a pretty careful routine.   If the stepper finds a better
		region of parameter space so that log(P) improves part way
		through the process, the routine will reset itself and begin
		again.

		@param ncw: how many times (or what fraction) of an ergodic
			exploration to make.
		@type ncw: int.
		@return: a L{position<mcmc.position_base>} at the end of the process.
		"""
		nc = _accum_erg()
		while nc.get() < ncw:
			self.x.step()
			self.logger.add(self.x, self.iter)
			nc.update(self.x)
			self.iter += 1
			self.maxloops -= 1
			if self.maxloops == 0:
				raise TooManyLoops, ("run_to_ergodic", nc.get(), ncw)
		return self.x.current()


	NC = 3
	def run_to_bottom(self, ns=3):
		m = self.x.np
		self.run_to_change(5+2*m, update_T=True)	# get it warmed up.
		before = self.run_to_change(ns, update_T=True)
		mid = self.run_to_change(ns, update_T=True)
		es = 0.0
		lock = Thr.allocate_lock()
		xchanged = Num.zeros(m, Num.Int)
		dotchanged = 0
		last_resetid = self.x.reset_id()
		while Num.sometrue(Num.less(xchanged,self.NC)) or es<1.0 or dotchanged<2*m:
			early = Num.sum(xchanged)<self.NC*m or es<0.8 or dotchanged<m
			try:
				after = self.run_to_change(ns, update_T=early)
			except TooManyLoops, x:
				raise TooManyLoops, ('run_to_bottom: s' % x, self.iter, es, dotchanged, m,
							Num.sum(Num.less(xchanged, self.NC)),
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

			es += self.x.ergodic() * ns

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
		return self.iter



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
