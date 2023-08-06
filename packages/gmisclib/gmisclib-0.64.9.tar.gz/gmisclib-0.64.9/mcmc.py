"""Markov-Chain Monte-Carlo algorithm.
This is a simulated annealing process which can
be used as an optimizer.

It may be imported as a normal module, and
you then normally create a bootstepper object
and call the step() method to take steps.

Or, you can use it as a script.
If so, you create your own module that implements
a few functions, and run mcmc.py .
It will import your module and call your functions.

The algorithm is not too different from amoeba_anneal, except for two
points:

	1. It keeps lots of points, typically more than 2*N of them, as opposed
   		to amoeba_anneal's N+1.

	2. It switches between two modes of operation:  In minimization mode,
  		it acts much like amoeba_anneal and preferentially tries to step from
  		the best vertex.     In MCMC mode, it starts its step randomly from
  		any vertex.     When it's going down-hill, it switches to
  		minimization mode to go down faster.    When it hasn't found a
  		significant improvement for a long time, it switches into MCMC mode
  		to produce the correct probability distribution.
  

As a script, it takes the following arguments:
	- o fff	Specifies a log file for some basic logging.

	- py mmm/mm	Specifies the module to load and to optimize.
		If the name contains a slash, it adds the base directory
		to the python search path, then looks for a module
		named by the last component.  If no slash, then it
		just looks up the module in PYTHONPATH.
		
	- NI NN	Sets the number of iterations.  Required, unless the
		module defines yourmod.NI.

	- --	Stops interpretation of the argument list.
		The remainder is passed to yourmod.init(), if
		it is defined, then to yourmod.start(), if that is
		defined.

It uses the following functions and variables:

	- yourmod.start(arglist, c)  (Not required).
		This is where you initialize the Monte-Carlo iteration.
		If you define yourmod.start(), it is passed the arglist,
		after the standard mcmc.py flags and arguments are removed
		from it.   Yourmod.start()
		must return a list of one or more starting vectors,
		(either a list of numpy arrays or a list of sequences
		of floats).    These starting vectors are used to seed the iteration.
		
		If it is not defined, mcmc.py will attempt to read a list
		of starting vectors in ascii format from the standard input.
		See mcmc._read().
		
	- yourmod.init(ndim, ni, c, arglist)   (Not required).
		This is primarily there to open a log file.
		Init is passed the remainder of the scripts argument
		list, after yourmod.start() looks at it.    It can do anything
		it wishes with the argument list.
		It can return an object or None.
		
		If it returns something other than None,
		that object will be used to call
		result_of_init.add( ) and
		result_of_init.finish(result_of_init).
		Finish() is there to print a summary or close a log files or similar.
		It is passed the standard output stream.

		Ndim is the length of the parameter vector,
		ni is the number of iterations,
		c is yourmod.c.

	- yourmod.resid(x, c)  (Either yourmod.logp() or yourmod.resid() is required.)

	- yourmod.logp(x, c)  (Either yourmod.logp() or yourmod.resid() is required.)
		These funtions are the thing which is to be optimized.
		Yourmod.log() returns the logarithm (base e) of the probability
		at position x.   X is a Numeric (possibly numarray) vector,
		and c is an arbitrary object that you define.  Often, c contains
		your data.
		
		Yourmod.logp() should return None if x is a silly value.  Note that
		the optimizer will tend to increase values of logp.  It's a maximizer,
		not a minimizer!
		
		If you give yourmod.resid() instead, logp() will be calculated
		as -0.5 times the sum of the squares of the residuals.   It should
		return a Numeric/numarray vector.  It may return None, which will
		cause the optimizer to treat the position as extremely bad.
		
	- yourmod.log(result_of_init, i, p, w)   (Not required).
		This is basically a function to log your data.
		No return value.    It is called at every step and
		passed the result of yourmod.init() (which might
		be a file descriptor to write into).  It is also passed the iteration
		count, i, the current parameter vector, p, and w, which is reserved
		for possible future use.


	- yourmod.NI  (required unless the -NI argument is given on the command line)
		Specifies how many iterations.  This is an integer.

	- yourmod.STARTLOW (not required).  Integer 0 or 1.
		If true, the iteration is started from the largest value of logp
		that is known.

	- yourmod.c	(required).
		This is an arbitrary object that is passed into yourmod.resid() or yourmod.logp().
		Often, it contains data or parameters for these functions,
		but it can be None if you have no need for it.

	- yourmod.V	(Not required)
		This specifies the covariance matrix that is used to hop from one
		test point to another.   It is
		a function that takes the result of yourmod.start() and returns
		a Numeric/numarray 2-dimensional square matrix,

		If it is not specified, mcmc will use some crude approximation
		and will probably start more slowly, but should work OK.
		If it is not specified and yourmod.start() returns only
		one starting position, then it will just use an identity matrix
		as the covariance matrix, and it might still work, but
		don't expect too much.
"""
from __future__ import with_statement

import sys
import math
import random
import Num
import multivariate_normal as MVN
import gpkmisc
import die
import g_implements
import types
import bisect
import threading

Debug = 0
MEMORYS_WORTH_OF_PARAMETERS = 1e8

def _logp1(x, c):
	# print "x=", x, "c=", c
	# print "type=", type(x), type(c)
	return -Num.sum(x*x*c*c)


def _logp2(x, c):
	r = Num.identity(x.vec().shape[0], Num.Float)
	r[0,0] = 0.707107
	r[0,1] = 0.707107
	r[1,0] = -0.707107
	r[1,1] = 0.707107
	xt = Num.matrixmultiply(x, r)
	return _logp1(xt, c)


class problem_definition(object):
	"""This class implements the problem to be solved.
	It's overall function in life is to compute the probability that a given
	parameter vector is acceptable.    Mcmc.py then uses that to run a
	Markov-Chain Monte-Carlo sampling.
	Often, you would
	want to derive a class and override all the functions defined here.
	Also, you may well want to define functions of your
	own here.
	
	For instance, it can be a good idea to define a function
	"model" that computes the model that you are fitting to data
	(if that is your plan).   Then logp() can be something
	like -Num.sum((self.model()-self.data)**2).
	Also, it can be good to define a "guess" function that computes
	a reasonable initial guess to the parameters, somehow.
	"""

	@g_implements.make_optional
	@g_implements.make_varargs
	def __init__(self, logp_fcn, c, fixer=None):
		self.c = c
		self._fixer = fixer
		# assert logp_fcn is None or callable(logp_fcn)
		assert callable(logp_fcn)
		self.lpf = logp_fcn

	def logp(self, x):
		"""
		@param x:a parameter vector
		@type x: numpy.ndarray
		@return: The log of the probability that the model assigns to parameters x.
		@rtype: float
		@raise NotGoodPosition: This exception is used to indicate that the position
			x is not valid.   This is equivalent to returning an extremely negative
			logp.
		"""
		return (self.lpf)(x, self.c)
	
	def fixer(self, x):
		"""Fixer() is called on each candidate position
		vector.    Generally, it is used to restrict the possible
		solution space by folding position vectors that escape outside the solution space back into
		the solution space.    It can also allow for symmetries in equations.

		Formally, it defines a convex region.   All vectors outside the region are mapped
		into the region, but the mapping must be continuous at the boundary.
		(More precisely, logp(fixer(x)) must be continuous everywhere that logp(x) is continuous,
		including the boundary.)   For instance, mapping x[0] into abs(x[0]) defines a convex region
		(the positive half-space), and the mapping is continuous near x[0]=0.

		Additionally, it may re-normalize parameters at will subject to the restriction
		that logp(fixer(x))==logp(x).
		For instance, it can implement a constraint that sum(x)==0 by mapping
		x into x-average(x), so long as the value of logp() is unaffected by that
		substitution.
		other folds can sometimes lead to problems.

		@param x:a parameter vector
		@type x: numpy.ndarray
		@return: a (possibly modified) parameter vector.
		@rtype: numpy.ndarray
		@attention: Within a convex region (presumably one that contains the optimal x),
			fixer must *not* change the value of logp(): logp(fixer(x)) == logp(x).

		@raise NotGoodPosition: This exception is used to indicate that the position
			x is not valid.   Fixer has the option of either
			mapping invalid parameter vectors into valid ones
			or raising this exception.
		"""
		if self._fixer is not None:
			return (self._fixer)(x, self.c)
		return x

	@g_implements.make_optional
	def log(self, p, i):
		"""Some code calls this function every iteration
		to log the current state of the MCMC process.
		@param p: the current parameter vector, and
		@param i: an integer iteration counter.
		@return: nothing.
		"""
		pass

	@g_implements.make_optional
	def guess(self):
		"""Some code calls this function at the beginning
		of the MCMC process to seed the iteration.
		@return: a list of guess vectors; each guess vector is
			suitable for passing to self.fixer() or self.logp() as x.
		"""
		pass



_Ntype = type(Num.zeros((1,), Num.Float))



class position_base(object):
	"""This class is used internally in the MCMC sampling process to
	represent a position.   It stores a parameter vector, a reference to
	the problem definition, and (optionally) caches computed values
	of log(P).
	"""
	@g_implements.make_optional
	def __init__(self, x, problem_def):
		"""You need this function and
		this signature if you are going to pass
		it to make_list_of_positions(), but not necessarily
		otherwise.
		"""
		g_implements.check(problem_def, problem_definition)
		self.pd = problem_def
		# print "position:x=", x
		tmp = Num.array(x, Num.Float, copy=True)
		tmp = self.pd.fixer(tmp)
		assert isinstance(tmp, _Ntype), "Output of fixer() is not numpy array."
		assert tmp.shape == x.shape, "Fixer output[%s] must match shape of input[%s]." % (str(tmp.shape),  str(x.shape))
		# self.x = Num.array(tmp, copy=True)
		self.x = tmp
		self._uid = hash(self.vec().tostring())


	# def __deepcopy__(self, memo):
		# """Don't copy andy deeper than this."""
		# return position_base(self.x, self.pd)


	def logp(self):
		"""Compute the log of the probability for the position.
		"""
		raise RuntimeError, "Virtual Function"


	def logp_nocompute(self):
		"""Shows a recent logp value.  It does not compute
		a value unless none has ever been computed.
		"""
		raise RuntimeError, "Virtual Function"


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount.
		@param shift: How much of a move to make to the new position.
		@type shift: numpy.ndarray
		@param logp: (optional)  If this is supplied, is is used to set the
			log(P) value for the newly created position structure.
		@type logp: float or None
		@return: a new position
		@rtype: L{position_base} or a subclass
		"""
		raise RuntimeError, "Virtual Function"


	def prms(self):
		"""The result of this function is to be handed to problem_definition.logp().
		This result must contain all the information specifying the position.
		Normally, this is a vector of floats, but concievably, you could include other information.
		"""
		return self.x


	def vec(self):
		"""Returns a numpy vector, for mathematical purposes.
		The result should contain all the information specifying the position;
		if not all, it should at least contain all the information that can be
		usefully expressed as a vector of floating point numbers.

		Normally, self.vec() and self.prms() are identical.
		"""
		return self.x


	@g_implements.make_optional
	def __repr__(self):
		return '<POSbase %s>' % str(self.x)


	def __cmp__(self, other):
		"""This is used when the archive is sorted."""
		dd = 0
		try:
			a = self.logp_nocompute()
		except NotGoodPosition:
			dd -= 2
		try:
			b = other.logp_nocompute()
		except NotGoodPosition:
			dd += 2
		return dd or cmp(a, b)


	def uid(self):
		return self._uid


class position_repeatable(position_base):
	"""This is for the common case where logp is a well-behaved
	function of its arguments.
	"""
	EPS = 1e-7
	HUGE = 1e38
	CACHE_LIFE = 50
	# CACHE_LIFE = 1	# For debugging only.

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		position_base.__init__(self, x, problem_def)
		if logp is not None and not (logp < self.HUGE):
			raise ValueError("Absurdly large value of logP", logp, self.x)
		self.cache = logp
		if logp is None:
			self.cache_valid = -1
		else:
			self.cache_valid = self.CACHE_LIFE
		if random.random() < 0.01:
			tmp = position_repeatable(self.x, problem_def)
			tlp = tmp.logp()
			slp = self.logp()
			if abs(tlp - slp) > 0.1 + self.EPS*abs(tlp+slp):
				# Ideally, EPS will be zero. But, you sometimes get roundoff
				# errors in the fixer early on in an optimization when the fit
				# is still awful.  So, you might end up being non-idempotent,
				# but only for a set of parameters that are so wild and awful
				# that no one really cares.   This is a bit of a kluge, but not a bad one.
				raise ValueError, "Fixer is not idempotent.  Logp changes from %s to %s." % (self.logp(), tmp.logp())
				


	def invalidate_cache(self):
		"""This can be called when the mapping between parameters (x)
		and value changes.    It's a milder version of position_history_dependent.
		"""
		self.cache_valid = -1


	def logp(self):
		if self.cache_valid <= 0:
			logp = self.pd.logp(self.prms())
			if not (logp is None or logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			if(self.cache_valid==0 and
				((self.cache is None)!=(logp is None)
				or
				abs(logp - self.cache) > 0.1 + 1e-8*(abs(logp)+abs(self.cache))
				)):
				raise ValueError, 'Recomputing position cache; found mismatch %s to %s' % (self.cache, logp)
			self.cache = logp
			self.cache_valid = self.CACHE_LIFE
		self.cache_valid -= 1
		if self.cache is None:
			raise NotGoodPosition
		return self.cache

	
	def logp_nocompute(self):
		if self.cache_valid < 0:
			return self.logp()
		if self.cache is None:
			raise NotGoodPosition
		return self.cache


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_repeatable(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if self.cache_valid > 0:
			s = str(self.cache)
		elif self.cache_valid == 0:
			s = "<cache expired>"
		else:
			s = "<uncomputed>"
		return '<POSr %s -> %s>' % (str(self.prms()), s)



class position_nonrepeatable(position_base):
	"""This is for the (unfortunately common) case where logp
	is an indpendent random function of its arguments.
	"""
	HUGE = 1e38

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		position_base.__init__(self, x, problem_def)
		if logp is None:
			self.cache = []
		else:
			if not (logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache = [ logp ]
		self.CSIZE = 5



	def logp(self):
		if random.random() > self.CSIZE / float(self.CSIZE + len(self.cache)): 
			logp = random.choice(self.cache)
		else:
			logp = self.pd.logp(self.prms())
			if not (logp is None or logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache.append(logp)
		if logp is None:
			raise NotGoodPosition
		return logp


	def logp_nocompute(self):
		if self.cache:
			tmp = random.choice(self.cache)
			if tmp is None:
				raise NotGoodPosition
		else:
			tmp = self.logp()
		return tmp


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_nonrepeatable(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if len(self.cache):
			s1 = ""
			mn = None
			mx = None
			for q in self.cache:
				if q is None:
					s1 = "BAD or"
				else:
					if mx is None or q>mx:
						mx = q
					if mn is None or q<mx:
						mn = q
			s = "%s%g to %g" % (s1, mn, mx)
		else:
			s = "<uncomputed>"
		return '<POSnr %s -> %s>' % (str(self.prms()), s)

class _empty(object):
	pass


class position_history_dependent(position_base):
	"""This is for the case where logp is a history-dependent
	function of its arguments.   This is the most general, most
	expensive case.
	"""
	EMPTY = _empty
	HUGE = 1e38

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		position_base.__init__(self, x, problem_def)
		if logp is None:
			self.cache = self.EMPTY
		else:
			if not (logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache = logp



	def logp(self):
		logp = self.pd.logp(self.prms())
		if not (logp is None or logp < self.HUGE):
			raise ValueError("Absurdly large value of logP", logp, self.x)
		self.cache = logp
		if logp is None:
			return NotGoodPosition
		return logp


	def logp_nocompute(self):
		if self.cache is self.EMPTY:
			return self.logp()
		if self.cache is None:
			return NotGoodPosition
		return self.cache


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_history_dependent(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if self.cache is self.EMPTY:
			s = "<uncomputed>"
		else:
			s = str(self.cache)
		return '<POSr %s -> %s>' % (str(self.prms()), s)


class T_acceptor(object):
	def __init__(self, T=1.0):
		assert T >= 0.0
		self._T = T

	def T(self):
		return self._T

	def __call__(self, delta):
		return delta > -self._T*random.expovariate(1.0)


class stepper(object):
	"""This is your basic stepper class that incrementally will
	give you a Markov-Chain Monte-Carlo series of samples from
	a probability distribution.
	"""

	@g_implements.make_varargs
	def __init__(self):
		self.since_last_rst = 0
		self.resetid = 0
		self.last_reset = None
		# self.last_failed should reflect the success or failure of the most recently
		# completed step.   It is None if the last step succeeded; it is the
		# most recently rejected position object if the last step failed.
		self.last_failed = None
		self.lock = threading.RLock()
		#: Acceptable is a function that decides whether or not a step is OK.
		#: You can replace it if you want.
		self.acceptable = T_acceptor(1.0)


	def step(self):
		"""In subclasses, this takes a step and returns 0 or 1,
		depending on whether the step was accepted or not."""
		self.since_last_rst += 1
		return None

	def prms(self):
		return self.current().prms()

	def current(self):
		"""Returns the current position.  (An instance of position.)"""
		raise RuntimeError, "Virtual Function"

	def prmlist(self):
		"""Returns all stored positions."""
		raise RuntimeError, "Virtual Function"
	
	def status(self):
		"""Provides some printable status information in a=v; format."""
		raise RuntimeError, "Virtual Function"

	
	def reset(self):
		"""Called internally to mark when the optimization
		has found a new minimum.   [NOTE: You might also call it
		if the function you are minimizing changes.]
		"""
		# print 'stepper.reset', threading.currentThread().getName()
		with self.lock:
			self.since_last_rst = 0
			self.resetid += 1

	def reset_id(self):
		return self.resetid

	def needs_a_reset(self):
		"""Decides if we we need a reset.    This checks
		to see if we have a new record logP that exceeds
		the old record.   It keeps track of the necessary
		paperwork.
		"""
		current = self.current()
		# print 'stepper.needs_a_reset', threading.currentThread().getName()
		with self.lock:
			if self.last_reset is None:
				self.last_reset = current
				rst = False
			else:
				rst = current.logp_nocompute() > self.last_reset.logp_nocompute() + self.acceptable.T()*0.5
				# rst = current.logp_nocompute() > self.last_reset.logp_nocompute()
				if rst:
					self.last_reset = current
		if rst and Debug>1:
			print '# RESET: logp=', current.logp_nocompute()
		return rst


	def _set_failed(self, f):
		with self.lock:
			self.last_failed = f
			if f is not None and self.archive.sorted and f.logp_nocompute()>self.archive.lop[0].logp_nocompute():
				self.archive.append(f, True)

	def current(self):
		with self.lock:
			return self._current

	
	def _set_current(self, newcurrent):
		with self.lock:
			self._current = newcurrent



class adjuster(object):
	Z0 = math.log(10.0)
	DZ = 0.3
	TOL = 0.2
	STABEXP = 1.0

	def __init__(self, F, alpha, vscale, vse=0.0, vsmax=1e30):
		assert 0.0 < F < 1.0
		self.lock = threading.Lock()
		self.alpha = alpha
		self.vscale = vscale
		self.F = F
		# self.np = np
		self.state = 0
		self.vse = vse
		self.reset()

		#: Used when the acceptance probability is larger than 25%.
		#: Large acceptance probabilities
		#: can happen if the probability is everywhere about
		#: equal.   (E.g. a data fitting problem with almost
		#: no data):
		self.vsmax = vsmax
		# print "NEW ADJUSTER"

	def reset(self):
		# print 'adjuster.reset', threading.currentThread().getName()
		with self.lock:
			self.z = self.Z0
			self.since_reset = 0
			self.ncheck = self._calc_ncheck()
			self.blocknacc = 0
			self.blockntry = 0
		# print "#ADJUSTER RESET"

	def _calc_ncheck(self):
		# This is the fewest samples where you could possibly
		# detect statistically significant deviations
		# from getting a fraction self.F of steps accepted.
		assert self.z >= self.Z0
		ss =  max( -self.z/math.log(1-self.f()), -self.z/math.log(self.f()) )
		assert ss > 3.0
		return int(math.ceil(max(ss, self.alpha*self.since_reset)))
	
	def f(self):
		"""This describes how the desired fraction of accepted steps should
		depend on self.vscale.   The logic behind this is that the boot
		stepper only works efficiently if self.vscale approx 1.
		If self.vscale < 1, we might as well allow a smaller acceptance probability
		in the hopes of getting a larger vscale.
		This has the side-benefit of avoiding vscale going to zero if (for
		some reason like a corner) the acceptance probability is always
		smaller than self.F.
		"""
		return self.F * min(1.0, self.vscale**self.vse)


	def inctry(self, accepted):
		# print 'adjuster.inctry', threading.currentThread().getName()
		with self.lock:
			self.since_reset += 1
			self.blockntry += 1
			self.blocknacc += accepted
	
			# Only check occasionally.
			if self.blockntry > self.ncheck:
				self._inctry_guts()


	def _inctry_guts(self):
		"""Called under lock!
		We check that the observed fraction of accepted
		steps is consistent with a Binomial distribution.
		If not, we try updating self.vscale.
		"""
		EPS = 1e-6
		Flow = self.f() * (1.0 - self.TOL)
		Fhi = self.f() * (1.0 + self.TOL)
		lPH0low = self.blocknacc*math.log(Flow) + (self.blockntry-self.blocknacc)*math.log(1-Flow)
		lPH0hi = self.blocknacc*math.log(Fhi) + (self.blockntry-self.blocknacc)*math.log(1-Fhi)
		Phat = (self.blocknacc + EPS)/(self.blockntry + 2*EPS)
		sigmaP = math.sqrt(self.f() * (1-self.f()) / self.blockntry)
		lPH1 = self.blocknacc*math.log(Phat) + (self.blockntry-self.blocknacc)*math.log(1-Phat)
		# print '#NCHECK bnacc=', self.blocknacc, self.blockntry, lPH0low, lPH0hi, lPH1, self.z

		if (Phat>Fhi and lPH1-lPH0hi > self.z) or (Phat<Flow and lPH1-lPH0low > self.z):
			# The fraction of accepted steps is inconsistent with the range
			# from Flow to Fhi -- in other words, we're certain the acceptance
			# rate is substantially wrong.

			delta = math.log(Phat/self.f())
			delta = min(max(delta, -self.TOL), self.TOL)
			self.vscale *= math.exp(delta*self.STABEXP)
			if self.vscale > self.vsmax:
				self.vscale = self.vsmax
			if Debug>2:
				print '#NCHECK step acceptance rate is %.2f vs. %.2f:' % (Phat, self.f()), 'changing vscale to', self.vscale
				print '#NCHECK ADJ vscale=', self.vscale, self.z, self.blocknacc, self.blockntry, delta
			self.blockntry = 0
			self.blocknacc = 0
			self.state = -1
			self.ncheck = self._calc_ncheck()
		elif Phat>Flow and Phat<Fhi and 2.0*sigmaP/self.f() < self.TOL:
			# We're as accurate as we need to be.
			# Therefore, we might as well restart the counters
			# in case the process is non-stationary.
			self.blockntry = 0
			self.blocknacc = 0
			self.state = 1
			self.ncheck = self._calc_ncheck()
			# print '#NCHECK close enough', 'phat=', Phat, 'sigmaP=', sigmaP
		else:
			# Doing OK.  The step acceptance rate is not
			# known to be incorrect.
			self.z += self.DZ
			self.state = 0
			self.ncheck = self.blockntry + self._calc_ncheck()
			# print "#NCHECK OK", self.ncheck, 'z=', self.z


	def vs(self):
		"""We stick in the factor of random.lognormvariate()
		so that all sizes of move are possible and thus we
		can prove that we can random-walk to any point in
		a connected region.   This makes the proof of
		ergodicity simpler.
		"""
		assert type(self.vscale)==types.FloatType
		return random.lognormvariate(0.0, self.TOL/2.0)*self.vscale


	def status(self):
		with self.lock:
			tmp = (self.blocknacc, self.blockntry, self.state)
		return tmp






def _start_is_list_a(start):
	"""Is the argument a sequence of numpy arrays?
	"""

	for (i, tmp) in enumerate(start):
		if not isinstance(tmp, _Ntype):
			if i > 0:
				raise TypeError, "Sequence is not all the same type"
			return False
	return len(start) > 0


def _start_is_list_p(start):
	"""Is the argument a sequence of position_base objects?
	"""

	for (i, tmp) in enumerate(start):
		if not g_implements.impl(tmp, position_base):
			if i > 0:
				raise TypeError, "Sequence is not all the same type"
			return False
	return len(start) > 0



class NoBoot(RuntimeError):
	def __init__(self):
		RuntimeError.__init__(self, "Can't find bootstrap points")

class NotGoodPosition(RuntimeError):
	def __init__(self, *s):
		RuntimeError.__init__(self, *s)



def make_list_of_positions(x, PositionClass, problem_def):
	"""Turn almost anything into a list of position_base objects.
	You can hand it a sequence of numpy vectors
	or a single 1-dimensional numpy vector;
	a sequence of position_base objects
	or a single 1-dimensional position_base object.

	@precondition: This depends on PositionClass being callable as
		PositionClass(vector_of_doubles, problem_definition).
	"""
	o = []
	if _start_is_list_a(x):
		assert len(x) > 0, "Zero length list of arrays."
		for t in x:
			if len(o) > 0:
				assert t.shape == (o[0].vec().shape[0],)
			# If the parameters are identical,
			# we can share position structures,
			# and reduce the number of times we need
			# to evaluate logp(x, c).
			if len(o)>0 and Num.alltrue(Num.equal(o[-1].vec(), t)):
				# print 'SAME:', t, self.current()
				o.append( o[-1] )
			else:
				# print 'DIFF:', t
				o.append( PositionClass(t, problem_def) )
	elif _start_is_list_p(x):
		assert len(x) > 0, "Zero length list of positions."
		o = []
		for t in x:
			g_implements.check(t, PositionClass)
			if len(o) > 0:
				assert t.vec().shape[0] == (o[0].vec().shape[0],)
			if len(o)>0 and Num.alltrue(Num.equal(t.vec(), o[-1].vec())):
				o.append( o[-1] )
			else:
				# print 'DIFF:', t
				o.append( t )
	elif g_implements.impl(x, PositionClass):
		o = [x]
	elif isinstance(x, _Ntype) and len(x.shape)==1:
		o = [ PositionClass(x, problem_def) ]
	else:
		raise TypeError, "Cannot handle type=%s for x.  Must implement %s or be a 1-dimensional numpy array." % (type(x), type(PositionClass))
	return o



def _check_list_of_positions(x):
	if not isinstance(x, list):
		raise TypeError, "Not a List (should be a list of positions)"
	for (i, t) in enumerate(x):
		failure = g_implements.why(t, position_base)
		if failure is not None:
			raise TypeError, "x[%d] does not implement position_base: %s" % (i, failure)


class hashcounter_c(dict):
	def incr(self, x):
		try:
			self[x] += 1
		except KeyError:
			self[x] = 1

	def decr(self, x):
		tmp = self[x]
		if tmp == 1:
			del self[x]
		elif tmp < 1:
			raise ValueError("More decrements than increments", x)
		else:
			self[x] = tmp-1





class Archive(object):
	"""This maintains a list of all the recent accepted positions."""
	#: Always keep the list of positions sorted.
	#: This improves mimimization performance at the cost of a distorted probability distribution.
	SSALWAYS = 'always'
	#: Never sort the list.    Best if you really want an exact Monte Carlo distribution.
	SSNEVER = 'neversort'
	#: Sort the list only when logp() is making substantial improvements.
	SSAUTO = 'auto'
	#: Start by sorting positions, then go to SSAUTO.
	SSLOW = 'startlow'

	def __init__(self, lop, np_eff, sort=SSAUTO, maxdups=-1, maxArchSize=None, alpha=None):
		assert sort in (self.SSLOW, self.SSNEVER, self.SSAUTO, self.SSALWAYS)
		assert len(lop) > 0
		self.lop = lop
		self.sortstrategy = sort
		self.sorted = sort in [self.SSLOW, self.SSALWAYS]
		if self.sorted:
			self.sort()
		self.np_eff = np_eff
		self.since_last_rst = 0
		self.lock = threading.Lock()
		assert maxdups > 0
		self.maxdups = maxdups
		self._hashes = hashcounter_c()
		for p in self.lop:
			self._hashes.incr(p.uid())

		if maxArchSize is None:
			maxArchSize = MEMORYS_WORTH_OF_PARAMETERS // self.np_eff
		#: The minimum length for the archive.  This is chosen to be big enough so that
		#: all the parallel copies probably span the full parameter space.
		self.min_l = self.np_eff + int(round(3*math.sqrt(self.np_eff))) + 7
		if maxArchSize < self.min_l:
			raise ValueError, "maxArchSize is too small for trustworthy operation: %d < min_l=%d (npeff=%d)" % (maxArchSize, self.min_l, self.np_eff)
		self.max_l = maxArchSize
		self.alpha = alpha


	def distinct_count(self):
		with self.lock:
			return len(self._hashes)
	

	def prmlist(self):
		with self.lock:
			return list(self.lop)


	def sort(self):
		"""Called under lock."""
		if self.sorted or self.sortstrategy==self.SSNEVER:
			return
		if Debug:
			die.info( '# Sorting archive' )
		# This uses position.__cmp__():
		self.lop.sort()
		self.sorted = True


	def reset(self):
		"""We sort the archive to speed the convergence to
		the best solution.   After all, if you've just
		gotten a reset, it is likely that you're not at the
		bottom yet, so statistical properties of the distribution
		are likely to be irrelevant.
		"""
		# print 'Archive.reset', threading.currentThread().getName()
		with self.lock:
			self.sort()
			self.truncate(self.min_l)
			self.since_last_rst = 0
	

	def __len__(self):
		with self.lock:
			return len(self.lop)


	def choose(self):
		# print 'Archive.lock', threading.currentThread().getName()
		with self.lock:
			return random.choice( self.lop )


	def truncate(self, desired_length):
		"""Desired length is in terms of the number of distinct
		positions.   Called under lock.
		"""
		assert len(self.lop) > 0
		assert len(self._hashes) <= len(self.lop)
		assert (len(self._hashes)>0) == (len(self.lop)>0)

		j = 0
		while len(self._hashes) > desired_length:
			self._hashes.decr(self.lop[j].uid())
			j += 1
		assert j <= len(self.lop)
		if j > 0:
			self.truncate_hook(self.lop[:j])
			self.lop = self.lop[j:]
			if Debug > 1:
				die.info('Truncating archive from %d by %d' % (len(self.lop), j))
		elif Debug > 1:
			die.info('Truncate: max=%d, len=%d, nothing done' % (desired_length, len(self.lop)))
		assert len(self._hashes) <= len(self.lop)
		# There is a possibility that we have truncated the current position.
		# I wonder if that's a problem?


	def _too_many_dups(self, uid):
		"""Called under lock."""
		if not self.lop or self.maxdups<0:
			return False
		st = max(len(self.lop) - self.maxdups, 0)
		for i in range(st, len(self.lop)):
			if self.lop[i].uid() != uid:
				return False
		return True


	def append(self, x, forbid_dups):
		"""Adds stuff to the archive, possibly sorting the
		new information into place.   It updates all kinds of
		counters and summary statistics.

		@param x: A position to (possibly) add to the archive.
		@type x: L{position_base}
		@param forbid_dups: Don't add duplicates to the archive.
		@type forbid_dups: boolean
		@return: A one-letter code indicating what happened.  'f' if x
			is a duplicate and duplicates are forbidden.
			'd' if it is a duplicate and there have been
			too many duplicates lately.
			'a' otherwise -- x has been added to the archive.
		@rtype: str
		"""
		# print 'Archive.append', threading.currentThread().getName()
		with self.lock:
			self.since_last_rst += 1

			assert len(self._hashes) <= len(self.lop)
			uid = x.uid()
			if forbid_dups and uid in self._hashes:
				return 'f'
			if self._too_many_dups(uid):
				# We don't want the clutter up the archive
				# with duplicates until the step sizes are
				# well established.
				if Debug>1:
					print 'Too many duplicates (more than %d): %x not archived.' % (
						self.maxdups, uid
						)
				assert len(self._hashes) <= len(self.lop)
				return 'd'
			self._hashes.incr(uid)

			if not self.sorted or self.sortstrategy==self.SSNEVER:
				self.lop.append(x)
				self.sorted = False
			else:
				# This uses position.__cmp__():
				bisect.insort_right(self.lop, x)
				# We can't do the following check because (a) it can
				# fail for position_nonrepeatable, and (b) it triggers
				# extra evaluations of logp(), which can be expensive:
				# assert self.lop[-1].logp() >= self.lop[0].logp()
				if self.since_last_rst > 2*self.np_eff and self.sortstrategy!=self.SSALWAYS:
					self.sorted = False
					if Debug:
						die.info( '# Archive sorting is now off' )
			self.append_hook(x)
			if Debug > 1:
				die.info('Archive length=%d' % len(self.lop))
			# print "self.lop=", self.lop
			assert len(self._hashes) <= len(self.lop)
			self.truncate( min(int( self.min_l + self.alpha*self.since_last_rst ),
						self.max_l)
					)
		return 'a'


	def append_hook(self, x):
		pass

	def truncate_hook(self, to_be_dropped):
		pass


class ContPrmArchive(Archive):
	def __init__(self, lop, np_eff, sort=Archive.SSAUTO, maxdups=-1, maxArchSize=None, alpha=None):
		"""Append_hook() is called for every element of the archive.
		That function can be replaced in a sub-class to accumulate
		some kind of summary.  Here, it is used to keep track of parameter
		means and standard deviations.
		"""
		Archive.__init__(self, lop, np_eff, sort=sort, maxdups=maxdups,
					maxArchSize=maxArchSize, alpha=alpha)
		self.p0 = lop[-1].vec()
		self.s = Num.zeros(self.p0.shape, Num.Float)
		self.ss = Num.zeros(self.p0.shape, Num.Float)
		for a in lop:
			self.append_hook(a)


	def append_hook(self, x):
		"""This accumulates parameter means and standard deviations.
		"""
		tmp = x.vec() - self.p0
		Num.add(self.s, tmp, self.s)
		Num.add(self.ss, tmp**2, self.ss)


	def truncate_hook(self, to_be_dropped):
		if len(to_be_dropped) > len(self.lop):
			# Take the opportunity to pick a better value of self.p0.
			self.p0 = self.s/(len(to_be_dropped) + len(self.lop))
			self.s = Num.zeros(self.p0.shape, Num.Float)
			self.ss = Num.zeros(self.p0.shape, Num.Float)
			for prms in self.lop:
				self.append_hook(prms)
		else:
			for prms in to_be_dropped:
				tmp = prms.vec() - self.p0
				Num.subtract(self.s, tmp, self.s)
				Num.subtract(self.ss, tmp**2, self.ss)

	def variance(self):
		with self.lock:
			n = len(self.lop)
			core = self.ss - self.s*self.s/n
			if not Num.alltrue(Num.greater(core, 0.0)):
				self.ss -= Num.minimum(0.0, core)
				if Debug > 0:
					die.warn('Zero stdev in archive.stdev for p=%s'
							% ','.join( ['%d' % q for q
								in Num.nonzero(Num.less_equal(core, 0.0))[0]
							])
						)
				return Num.ones(self.s.shape, Num.Float)
		assert n > 1
		assert Num.alltrue(Num.greater(core, 0.0))
		return core/(n-1)


class BootStepper(stepper):
	#: Targeted step acceptance rate.
	F = 0.25
	alpha = 0.1
	#: Limits the probability of taking a bootstrap step to PBootLim
	PBootLim = 0.9
	#: How many parameters does it take to fill up the machine's memory?
	#: Control of when to sort steps and when to run with honest Monte-Carlo:
	SSAUTO = ContPrmArchive.SSAUTO
	SSNEVER = ContPrmArchive.SSNEVER
	SSLOW = ContPrmArchive.SSLOW
	SSALWAYS = ContPrmArchive.SSALWAYS

	def __init__(self, lop, v, sort=SSAUTO, maxArchSize=None, parallelSizeDiv=1):
		"""@param maxArchSize: How many position vectors can be stored.  This is
			normally used to (loosely) enforce a memory limitation for large
			jobs.
		@param parallelSizeDiv: For use when there are several cooperating MCMC
			processes that share data.  When >1, this allows each process
			to have smaller stored lists.   Normally, parallelSizeDiv is
			between 1 and the number of cooperating processes.
		"""
		stepper.__init__(self)
		_check_list_of_positions(lop)
		stepper._set_current(self, lop[-1])
		#: The number of parameters:
		self.np = lop[0].vec().shape[0]
		#: In a multiprocessor situation, np_eff tells you how much data do you
		#: need to store locally, so that the overall group of processors
		#: stores enough variety of data.
		self.np_eff = (self.np+parallelSizeDiv-1)//parallelSizeDiv
		self.archive = ContPrmArchive(lop, self.np_eff, sort=sort, maxdups=int(round(4.0/self.F)),
						maxArchSize=maxArchSize, alpha=self.alpha)

		if not self.np > 0:
			raise ValueError, "Np=%d; it must be positive." % self.np
		if v.shape != (self.np, self.np):
			raise ValueError, "v must be square, with side equal to the number of parameters. Vs=%s, np=%d." % (str(v.shape), self.np)

		self.v = Num.array(v, Num.Float, copy=True)
		self.V = MVN.multivariate_normal(Num.zeros(v.shape[0], Num.Float),
								v)
		self.aB = adjuster(self.F, self.alpha, vscale=0.5, vse=0.5, vsmax=1.3)
		self.aV = adjuster(self.F, self.alpha, vscale=1.0)
		self.steptype = None


	def step(self):
		stepper.step(self)
		WBoot = min(self.archive.distinct_count(), self.F*self.since_last_rst)
		WV = self.np_eff
		P = min(self.PBootLim, WBoot/float(WBoot+WV))
		if random.random() < P:
			try:
				accepted = self.step_boot()
			except NoBoot:
				accepted = self.stepV()
		else:
			accepted = self.stepV()
		return accepted




	def prmlist(self):
		return self.archive.prmlist()

	# def last(self):
		# return self.archive.last()
		
	
	def status(self):
		with self.lock:
			o = ['a0vs=%g' % self.aB.vscale,
				'a0acc=%g; a0try=%g; a0state=%d' % self.aB.status(),
				'a1vs=%g' % self.aV.vscale,
				'a1acc=%g;  a1try=%g; a1state=%d' % self.aV.status(),
				'nboot=%d' % len(self.archive),
				'logP=%g' % self.current().logp_nocompute(),
				'type=%s' % self.steptype
				]
		return '; '.join(o) + ';'


	def stepV(self):
		self.steptype = 'stepV'
		vs1 = self.aV.vs()
		move = self.V.sample() * vs1
		if hasattr(self.archive, 'variance') and self.archive.distinct_count() >= min(5, self.np):
			move *= (self.archive.variance()/self.v.diagonal())**0.25

		# print "self.current()=", self.current()
		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except NotGoodPosition:
			if Debug>2:
				die.warn('StepV: NotGoodPosition')
			# self._set_failed( tmp )
			# Should I call self.aV.inctry(0) ?
			return 0
		if self.acceptable(delta):
			self._set_failed( None )
			accepted = 1
			if Debug>2:
				die.info('StepV: Accepted logp=%g' % tmp.logp_nocompute())
			# We cannot use self.lop[-1] for current because lop is
			# sometimes sorted.  When it is, the most recently added
			# position could end up anywhere in the list.   Thus, we keep
			# a separate self._current.
			self._set_current(tmp)
			self.aV.inctry(accepted)
		else:
			self._set_failed( tmp )
			accepted = 0
			if Debug>2:
				die.info('StepV: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))
			self.aV.inctry(accepted)
			self._set_current(self.current())
		return accepted


	def step_boot(self):
		self.steptype = 'step_boot'
		vs0 = self.aB.vs()
		assert vs0 < 10.0, "Vs0 too big!=%s" % str(vs0)
		if Debug>3:
			die.note('VsB', vs0)

		if len(self.archive) <= 2:
			# print 'NoBoot', len(self.archive)
			raise NoBoot
		p1 = self.archive.choose()
		p2 = self.archive.choose()
		# if p1 is p2:
		if p1.uid() == p2.uid():
			# print 'NoBoot dup'
			raise NoBoot

		# die.note('p1.prms', p1.prms())
		# die.note('p2.prms', p2.prms())
		move  = (p1.vec() - p2.vec()) * vs0
		# print '# move=', p1.prms(), p2.prms(), vs0, move

		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except NotGoodPosition:
			if Debug>2:
				die.warn('StepBoot: Nogood position')
			# self._set_failed( tmp )
			return 0
		if self.acceptable(delta):
			self._set_failed( None )
			accepted = 1
			if Debug>2:
				die.info('StepBoot: Accepted logp=%g' % tmp.logp_nocompute())
			self._set_current(tmp)
			self.aB.inctry(accepted)
		else:
			self._set_failed( tmp )
			accepted = 0
			if Debug>2:
				die.info('StepBoot: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))
			self.aB.inctry(accepted)
			self._set_current(self.current())
		return accepted



	def _set_current(self, newcurrent):
		g_implements.check(newcurrent, position_base)
		# print 'bootstepper.set_current', threading.currentThread().getName()
		stepper._set_current(self, newcurrent)
		out = []
		with self.lock:
			#: After a reset, the optimizer may not have good step directions,
			#: so there may be many failed steps.   Thus, you don't want to
			#: fill up the archive with lots of duplicates of the current position
			#: that are basically meaningless.    Thus, we forbid duplicates for
			#: a while.
			forbid_dups = self.since_last_rst < self.np_eff
			q = self.archive.append(newcurrent, forbid_dups=forbid_dups)
			out.append(q)
			if self.needs_a_reset():
				# Shorten the archive -- if we've found a new best
				# point, that makes it likely that we have not
				# yet converged.   Consequently, since were
				# probably not near stationarity, the old history
				# is probably useless.
				self.reset_adjusters()
				self.archive.reset()
				self.reset()
				out.append('r')
		return ''.join(out)


	def reset_adjusters(self):
		self.aB.reset()
		self.aV.reset()


	def ergodic(self):
		"""A crude measure of how ergodic the MCMC is.
		This is the inverse of how many steps it takes to cross the
		minimum in the slowest direction.
		"""
		if self.since_last_rst*self.aB.f() < self.np_eff:
			# Presumably, we are still stabilizing.
			# print '# SLR in ergodic'
			return 0.0
		if self.aB.state < 0:
			# The step size is known to be mis-adjusted,
			# so you cannot use it to compute a measure
			# of the ergodicity.
			# print '# state<0 in ergodic', self.aB.state
			return 0.0

		# This is calibrated from the equilibrium vscale from long runs
		# in 1-50 dimensional Gaussian problems.

		vsbar = 1.7/math.sqrt(self.np)	# Should this be np_eff ?
		vs = self.aB.vscale
		# print 'ergodic: vs=', vs, "erg=", min(1.0, vs/vsbar)**2
		return self.F * min(1.0, vs/vsbar) ** 2


	def set_sort_strategy(self, ss):
		tmp = self.archive.sortstrategy
		self.archive.sortstrategy = ss
		return tmp


def bootstepper(logp, x, v, c=None, sort=BootStepper.SSAUTO, fixer=None, repeatable=True):
	"""This is (essentially) another interface to the class constructor.
	It's really there for backwards compatibility.
	"""
	pd = problem_definition(logp_fcn=logp, c=c, fixer=fixer)
	position_constructor = [position_nonrepeatable, position_repeatable][repeatable]
	return BootStepper(make_list_of_positions(x, position_constructor, pd), v, sort=sort)

boot2stepper = bootstepper


def test():
	logp = _logp1
	# logp = _logp2
	start = [1.0, 2.0, 2, 9, 1]
	c = [10.0, 10.0, 10.0, 10.0, 0.1]
	V = Num.identity(len(c), Num.Float)
	# V = Num.array([[ 20.69626808,  20.6904984 ], [ 20.6904984,   20.69477235]])

	x = bootstepper(logp, start, V, c=c)

	v = Num.zeros(V.shape, Num.Float)
	for i in range(10000):
		x.step()
		p = x.vec()
		sys.stdout.writelines('%d ' % i)
		for j in range(x.vec().shape[0]):
			sys.stdout.writelines('%g ' % p[j])
		sys.stdout.writelines('\n')
		v += Num.outerproduct(p, p)
	
	v /= 10000.0
	sys.stderr.writelines(str( v ) + "\n")
	evalues, evec = Num.LA.eigh(v)
	sys.stderr.writelines("Eval: %s\n" % str(evalues))
	sys.stderr.writelines("Evec: %s\n" % str(evec))


def _print(fd, prefix, p):
	fd.writelines( ' '.join( [prefix] + [ '%g'%pj for pj in p ] ) )
	fd.writelines('\n')


def _read(fd):
	o = []
	for t in fd:
		if t.startswith('#'):
			continue
		t = t.strip()
		if t == '':
			continue
		o.append( Num.array( [float(x) for x in t.split() ],
					Num.Float)
			)
	np = o[-1].shape[0]
	# die.info("np=%d" % np)
	return o[ max(0, len(o)-2*np*np) : ]





def diag_variance(start):
	"""Hand this a list of vectors and it will compute
	the variance of each component, then return a diagonal
	covariance matrix.
	"""
	tmp = gpkmisc.vec_variance(start)
	if not Num.alltrue(Num.greater(tmp, 0.0)):
		raise ValueError, ("Zero variance for components %s"
					% ','.join(['%d'%q for q in
							Num.nonzero(1-Num.greater(tmp, 0.0))[0]
						]
						)
					)
	return gpkmisc.make_diag(tmp)


def logp_from_resid(x, c, resid_fcn):
	r = resid_fcn(x, c)
	if r is None:
		raise NotGoodPosition
	# return -Num.sum(Num.ravel(r)**2)/2.0
	return -Num.sum(r**2)/2.0


def go(argv, theStepper):
	"""Run the optimization, controlled by command line flags."""
	global Debug
	import load_mod
	if len(argv) <= 1:
		print __doc__
		return
	python = None
	out = None
	NI = None
	arglist = argv[1:]
	while len(arglist) > 0  and arglist[0][0] == '-':
		arg = arglist.pop(0)
		if arg == '-o':
			out = arglist.pop(0)
		elif arg == '-py':	# path/module
			python = arglist.pop(0)
		elif arg == '-NI':
			NI = int(arglist.pop(0))
		elif arg == '-debug':
			Debug += 1
		elif arg == '--':
			break
		else:
			die.die("Unrecognized flag: %s" % arg)
	
	assert python is not None, "Need to use the -py flag."

	mod = load_mod.load_named_module(python)
	print "# mod= %s" % str(mod)

	if out:
		logfd = open(out, "w")
	else:
		logfd = None

	mod_c = getattr(mod, "c", None)
	if not hasattr(mod, "start"):
		start = _read(sys.stdin)
	else:
		start = mod.start(arglist, mod_c)

	if hasattr(mod, 'logp'):
		logPfcn = mod.logp
	elif hasattr(mod, 'resid'):
		logPfcn = lambda x, c, m=mod: logp_from_resid(x, c, m.resid)
	else:
		die.die("Can't find logp() or resid() function in module.")

	if NI is None:
		NI = mod.NI
	print "# NI= %d" % NI


	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.start() changed c.
	if hasattr(mod, "V"):
		V = Num.asarray(mod.V(start, mod_c), Num.Float)
	elif _start_is_list_a(start) and len(start)>1:
		V = diag_variance(start)
	else:
		V = Num.identity(start[0].shape[0], Num.Float)

	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.V() changed c.
	if hasattr(mod, "init"):
		logptr = mod.init(V.shape[0], NI, mod_c, arglist)
	else:
		logptr = def_logger(V.shape[0], NI, mod_c, arglist)

	sort = getattr(mod, 'SORT_STRATEGY', BootStepper.SSAUTO)

	fixer = getattr(mod, 'fixer', None)

	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.init() changed c.
	sys.stdout.flush()
	x = theStepper(logPfcn, start, V, c=mod_c, sort=sort, fixer=fixer)

	sys.stdout.writelines('[P]\n')
	for i in range(NI):
		x.step()
		p = x.prms()
		sys.stdout.flush()
		if logfd is not None:
			logfd.writelines('# ' + x.status() + '\n')
			_print(logfd, '%d'%i , p)
			logfd.flush()
		if logptr is not None:
			logptr.add(p, i)
	if logptr is not None:
		logptr.finish(sys.stdout)


class def_logger:
	def __init__(self, ndim, ni, c, arglist):
		self.v = Num.zeros((ndim,ndim), Num.Float)
		self.n = 0
		self.NI = ni
		self.c = c
	
	def add(self, p, i):
		if i >= self.NI/10:
			self.v += Num.outerproduct(p, p)
			self.n += 1

	def finish(self, stdout):
		self.v /= float(self.n)
		sys.stdout.writelines('[V]\n')
		sys.stderr.writelines(str( self.v ) + "\n")
		evalues, evec = Num.LA.eigh(self.v)
		stdout.writelines('[Evals]\n')
		stdout.writelines("%s\n" % str(evalues))
		stdout.writelines('[Evecs]\n')
		stdout.writelines("%s\n" % str(evec))






if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	try:
		go(sys.argv, bootstepper)
	except:
		die.catch('Unexpected exception')
		raise
