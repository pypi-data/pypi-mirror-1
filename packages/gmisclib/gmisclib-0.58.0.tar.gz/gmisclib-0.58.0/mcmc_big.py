
"""An extension of mcmc that includes a new stepping algorithm.
"""

from __future__ import with_statement

import math
import random
from gmisclib import die
from gmisclib import mcmc
from gmisclib.mcmc import Debug


def _parab_interp_guts(x0, y0, x1, y1, x2, y2):
	xx01 = x0**2 - x1**2
	x01 = x0 - x1
	y01 = y0 - y1
	xx21 = x2**2 - x1**2
	x21 = x2 - x1
	y21 = y2 - y1
	
	b = (y01*xx21 - y21*xx01) / (xx21*x01 - xx01*x21) 
	a = (y01 - b*x01) / xx01
	c = y0 - a*x0**2 - b*x0
	return (a, b, c)


def pairmax(*xy):
	bestx, besty = xy[0]
	for (x,y) in xy[1:]:
		if y > besty:
			besty = y
			bestx = x
	return (bestx, besty)


def _parab_interp(x0, y0, x1, y1, x2, y2):
	xctr = (x0 + x1 + x2) / 3.0
	# print 'XY=', (x0, y0), (x1, y1), (x2, y2)
	x0 -= xctr
	x1 -= xctr
	x2 -= xctr

	# print 'xy=', (x0, y0), (x1, y1), (x2, y2)
	a, b, c = _parab_interp_guts(x0, y0, x1, y1, x2, y2)
	# print 'abc=', a, b, c
	mn = min(x0, x1, x2)
	mx = max(x0, x1, x2)
	w = mx - mn
	bestx= pairmax((x0,y0), (x1,y1), (x2,y2))[0]
	if a >= 0.0:
		# print 'A>0 !'
		return bestx + w*(random.random()-0.5)
	else:
		xmin = -b/(2*a)
		if min(abs(xmin-x0), abs(xmin-x1), abs(xmin-x2)) < 0.01*w:
			# Too close to replication of an existing point.
			return bestx + w*(random.random()-0.5)
		sigma = math.sqrt(-2.0/a)
		xtmp = random.normalvariate(xmin, sigma)
		# print 'xmin=', xmin, 'sigma=', sigma, '=> xtmp=', xtmp
		if -1.5*w < xtmp < 1.5*w:
			return xctr + xtmp
		return bestx + 1.5*w*(random.random()-0.5)

def test():
	a, b, c = _parab_interp_guts(0.0, 1.0, 1.0, 0.0, 2.0, 1.0)
	assert abs(a-1.0) < 0.001
	assert abs(-b/(2*a) - 1.0) < 0.001
	assert abs(c-1.0) < 0.001


test()

def find_closest_p(v, *vp):
	"""Searches a list of (v,p) pairs and finds the one whose v
	is closest to the first argument.   Returns
	(v,p) of the closest pair.
	"""
	assert len(vp) > 0
	vc, pc = vp[0]
	for (vi, pi) in vp[1:]:
		if abs(vi-v) < abs(vc-v):
			vc = vi
			pc = pi
	return (vc, pc)


class BootStepper(mcmc.BootStepper):
	def __init__(self, lop, v, sort=mcmc.BootStepper.SSAUTO,
				maxArchSize=None, parallelSizeDiv=1):
		mcmc.BootStepper.__init__(self, lop, v, sort=sort,
						maxArchSize=maxArchSize,
						parallelSizeDiv=parallelSizeDiv)
		self.aM = mcmc.adjuster(self.F, self.alpha, vscale=0.5, vse=0.5, vsmax=1.1)


	def step(self):
		mcmc.stepper.step(self)
		leff = min( self.archive.distinct_count(),	# Bootstrapping requires a big archive.
				self.F*self.since_last_rst + self.np_eff,	# Reduce P to 50% after a reset.
				self.PBootLim*self.np_eff		# Keeps P from becoming too large.
				)
		Wboot = leff
		Wmixed = leff
		WV = self.np_eff
		# Parabolic steps are a bootstrap method, so they needs a large archive.
		# But, Step_parab is not really Markov, so we only want to do it 
		# to help find the minimum after a reset.
		Wparab = min(self.archive.distinct_count(), max(0, self.np_eff-self.since_last_rst))
		W = Wboot + Wmixed + Wparab + WV
		Pboot = Wboot/W
		Pmixed = Pboot + Wmixed/W
		Pparab = Pmixed + Wparab/W

		P = random.random()
		try:
			if P < Pboot:
				accepted = self.step_boot()
			elif P < Pmixed:
				accepted = self.step_mixed()
			elif P < Pparab:
					# Note! This violates MCMC requirements!
					# The resulting probability distribution will not be correct
					# when step_parab() is used!
					accepted = self.step_parab()
			else:
				accepted = self.stepV()
		except mcmc.NoBoot:
			accepted = self.stepV()
		return accepted


	def reset_adjusters(self):
		self.aB.reset()
		self.aV.reset()
		self.aM.reset()


	def step_mixed(self):
		self.steptype = 'step_mixed'
		assert self.T >= 0.0
		vsm = self.aM.vs()
		vs0 = self.aB.vs() * vsm
		assert vs0 < 30
		vs1 = self.aV.vs() * 0.01 * vsm
		if Debug > 1:
			print 'step_mixed', 'vsm,0,1=', vsm, vs0, vs1

		if len(self.archive) <= 2:
			# print 'NoBoot', len(self.archive)
			raise mcmc.NoBoot
		p1 = self.archive.choose()
		p2 = self.archive.choose()
		if p1.uid() == p2.uid():
			# print 'NoBoot dup'
			raise mcmc.NoBoot

		if self.archive.distinct_count() >= min(5, self.np_eff):
			move = vs1 * (self.archive.variance()/self.v.diagonal())**(1./4.)

		move  = (p1.vec() - p2.vec()) * vs0 + vs1 * self.V.sample()
		tmp = self.current().new(move)
		if tmp.nogood():
			die.warn('Nogood position')
			self._set_failed( tmp )
			# Should I call self.aM.inctry(accepted) ?
			return 0
		delta = tmp.logp() - self.current().logp()
		if delta > -self.T*random.expovariate(1.0):
			self._set_failed( None )
			accepted = 1
			self._set_current(tmp)
			self.aM.inctry(accepted)
		else:
			self._set_failed( tmp )
			accepted = 0
			self.aM.inctry(accepted)
			self._set_current(self.current())
		return accepted



	def step_parab(self):
		self.steptype = 'step_parab'
		assert self.T >= 0.0
		# The parabolic fit will be degenerate if we pick vs0 too close
		# to either of the existing points.
		vs00 = self.aB.vs()
		while True:
			vs0 = random.normalvariate(0.0, vs00)
			if abs(vs0)>0.05 and abs(abs(vs0)-1)>0.05:
				break


		if len(self.archive) <= 2:
			raise mcmc.NoBoot
		p1 = self.current()
		p2 = self.archive.choose()
		if p1.uid() == p2.uid():
			raise mcmc.NoBoot

		vbase, pbase = find_closest_p(vs0, (0.0, p1), (1.0, p2))
		move  = (p2.vec() - p1.vec()) * (vs0-vbase)
		# This is a perfectly good MCMC step, at least when the
		# archive is large and well-annealed.
		tmp = pbase.new(move)
		if Debug > 2:
			print "step_parab: vs0=", vs0, "vbase=", vbase

		if tmp.nogood():
			die.warn('Nogood position')
			self._set_failed( tmp )
			return 0
		delta = tmp.logp() - self.current().logp()
		if delta < -self.T*random.expovariate(1.0):
			self._set_failed( tmp )
			accepted = 0
			self._set_current(self.current())
		else:
			accepted = 1
			self._set_failed( None )
			self._set_current(tmp)
		if delta < -self.T*(4.0 + 4.0*abs(p1.logp_nocompute()-p2.logp_nocompute())):
			# This step was unexpectedly awful.   It may not
			# be worth investing any more effort, and
			# the parabolic approximation may well be
			# not very good.
			if Debug > 1:
				print "step_parab: bailing out: delta=", delta
			return accepted

		vsnew = _parab_interp(0.0, p1.logp(), 1.0, p2.logp(), vs0, tmp.logp())
		vbase, pbase = find_closest_p(vsnew, (0.0, p1), (1.0, p2), (vs0, tmp))
		if Debug > 2:
			print "step_parab: interp v=", vsnew, "base=", vbase
		move  = (p2.vec() - p1.vec()) * (vsnew-vbase)
		tmp = pbase.new(move)
		delta = tmp.logp() - self.current().logp()

		if tmp.nogood():
			die.warn('Nogood position')
			self._set_failed( tmp )
			accepted = 0
		elif delta < -self.T*random.expovariate(1.0):
			self._set_failed( tmp )
			accepted = 0
			self._set_current(self.current())
		else:
			self._set_failed( None )
			accepted = 1
			self._set_current(tmp)
		return accepted



def bootstepper(logp, x, v, c=None, sort=BootStepper.SSAUTO, fixer=None, repeatable=True):
	"""This is (essentially) another interface to the class constructor.
	It's really there for backwards compatibility.
	"""
	pd = mcmc.problem_definition(logp_fcn=logp, c=c, fixer=fixer)
	position_constructor = [mcmc.position_nonrepeatable, mcmc.position_repeatable][repeatable]
	return BootStepper(mcmc.make_list_of_positions(x, position_constructor, pd), v, sort=sort)

diag_variance = mcmc.diag_variance
stepper = mcmc.stepper
problem_definition = mcmc.problem_definition
position_repeatable = mcmc.position_repeatable
position_nonrepeatable = mcmc.position_nonrepeatable
position_history_dependent = mcmc.position_history_dependent


if __name__ == '__main__':
	import sys
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	try:
		mcmc.go(sys.argv, bootstepper)
	except:
		die.catch('Unexpected exception')
		raise
