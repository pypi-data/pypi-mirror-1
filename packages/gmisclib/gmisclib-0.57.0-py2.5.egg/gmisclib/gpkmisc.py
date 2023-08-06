
import math
import sys

try:
	from Numeric_gpk import N_maximum, N_minimum, N_median, N_mean_ad,	\
			median_across, N_median_across, variance, stdev,	\
			set_diag,	\
			make_diag, limit, vec_variance, qform,	\
			KolmogorovSmirnov, interp, interpN
except ImportError, _x:
	if str(_x).startswith('cannot import name'):
		raise
	pass


def median(x):
	xx = sorted(x)
	n = len(xx)
	assert n > 0, "No data to median."
	return 0.5*(xx[n//2] + xx[(n-1)//2])


def avg(x):
	s = 0.0
	n = 0
	for t in x:
		s += t
		n += 1
	return s/float(n)


def median_ad(x):
	"""Median absolute deviation"""
	medn = median(x)
	return median( [ abs(t-medn) for t in x ] )
mad = median_ad


def mean_ad(x):
	medn = median(x)
	sum = 0.0
	for t in x:
		sum += abs(t-medn)
	return sum/float(len(x))


def geo_mean(*d):
	"""Geometric mean of its arguments."""
	s = 0.0
	for t in d:
		s += math.log(t)
	return math.exp(s/len(d))



def entropy(x):
	"""Compute the entropy of a list of probabilities."""
	e = 0.0
	ps = 0.0
	for p in x:
		assert p <= 1.0
		if p > 0.0:
			e -= p*math.log(p)
		ps += p
	assert 0.999 < ps < 1.001, "Probabilities must sum to one."
	return e


def resample(d):
	"""Bootstrap resampling.  Call this many times: each one
	returns a random resampling.
	"""
	import random
	o = []
	for i in range(len(d)):
		o.append( random.choice(d) )
	return o


def jackknife(d):
	"""Jackknife resampling.  Call this once.
	It returns a list of deleted lists."""
	for drop in range(len(d)):
		yield [ di for (i, di) in enumerate(d) if i!=drop ]






def Student_t_dens(x, n):
	"""From p.337 Statistical Theory by Bernard Lindgren."""

	from transcendental import gamma
	# http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/python/statistics.html	
	p = gamma((n+1)/2.0) * (1+x*x/n)**(-(n+1)/2.0) / (
			math.sqrt(n*math.pi)*gamma(n/2.0)
			)
	return p




_fcache = {}
def log_factorial(n):
	assert n >= 0
	try:
		lf = _fcache[n]
	except KeyError:
		lf = 0.0
		for i in range(2,n):
			lf += math.log(i)
		_fcache[n] = lf
	return lf


def log_Combinations(n, m):
	assert n >= m
	assert m >= 0
	return log_factorial(n) - log_factorial(m) - log_factorial(n-m)

def ComplexMedian(P):
	"""P is a list of complex numbers.
	This algorithm works by repeatedly stripping off the convex
	hull of the points.
	"""
	import convex_hull2d
	import cmath
	import dictops
	HUGE = 1e30
	EPS = 1e-7
	Q = dictops.dict_of_accums()
	for p in P:
		Q.add(p, 1.0)

	while len(Q) > 3:
		# print 'Q=', Q
		edge = convex_hull2d.convexHull(Q.keys())
		# print 'edge=', edge
		ee = (edge[-1],) + edge + (edge[0],)
		wt = {}
		for i in range(1,len(edge)+1):
			em = ee[i] - ee[i-1]
			ep = ee[i+1] - ee[i]
			# angle = cmath.log(em).imag - cmath.log(ep).imag
			if min(abs(ep), abs(em)) < EPS*max(abs(em), abs(ep)):
				angle = math.pi/2.0	#Kluge, mild.   Roundoff errors.
			else:
				angle = cmath.log(em/ep).imag
			# KLUGE AND ROUNDOFF WARNING!
			if angle <= 0.0 and angle > -0.5:
				angle = EPS	#KLUGE!  Awful!
			if angle < 0.0:
				angle += 2*math.pi
			if angle >= math.pi and angle<math.pi+0.5:
				angle = math.pi-EPS	# KLUGE!  Awful!
			# print 'angle=', angle, ee[i-1], ee[i], ee[i+1], 'pi=', math.pi
			assert angle>=0 and angle<=math.pi, "angle=%g" % angle
			wt[ee[i]] = angle
		fmin = HUGE
		for p in edge:
			f = Q[p]/wt[p]
			if f < fmin:
				fmin = f
		# print 'fmin=', fmin
		assert fmin > 0.0
		sum = complex()
		swt = 0.0
		for p in edge:
			fwp = fmin * wt[p]
			# print 'Subtracting wt of ', fwp, 'from Q[', p, ']=', Q[p]
			swt  += fwp
			sum += p * fwp
			if Q[p] > fwp+EPS:
				Q[p] -= fwp
				# print '\tQ[', p, ']=', Q[p]
			else:	# Q[p]<=fwp
				assert abs(Q[p]-fwp) < EPS
				# print 'Deleting Q[', p, ']=', Q[p]
				del Q[p]
		if len(Q) == 0:
			return sum/swt
	# print 'Qfinal=', Q
	sum = complex()
	w = 0.0
	for (p,n) in Q.items():
		sum += p*n
		w += n
	return sum/w



def testCM():
	def eq(a, b):
		tmp = abs(a-b)/(abs(a)+abs(b)) < 1e-6
		if not tmp:
			print 'eq fails: %s vs %s' % (str(a), str(b))
		return tmp
	print 'CM'
	assert eq(ComplexMedian([complex(1,0), complex(2,0), complex(3,0)]), 2)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4)]), 2.5)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4), complex(5)]), 3)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4), complex(4)]), 3)
	assert eq(ComplexMedian([complex(1,1), complex(2,2), complex(3,3), complex(4,4)]),
			complex(2.5,2.5))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1), complex(1,1)]),
			complex(0.5,0.5))
	assert eq( ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(1,1), complex(1,1)]),
			complex(1,1))
	assert eq( ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(1,1), complex(0.6,0.6)]),
			complex(0.6,0.6))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1), complex(1,1),
				complex(0,0), complex(2,0), complex(0,2), complex(2,2)]),
			complex(0.5,0.5))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1)]),
			complex(1./3., 1./3.))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(0,0), complex(2,0), complex(0,2)]),
			complex(0.3, 0.3))
	import cmath
	for N in [3, 4, 5, 6, 7, 8, 13, 40, 100, 2351]:
		print 'N=', N
		assert eq(ComplexMedian( [ 1+cmath.exp(2*cmath.pi*1j*float(q)/N)
						for q in range(N) ]),
				complex(1.0, 0.0)
				)





import Queue
import threading
class threaded_readable_file(object):
	QSIZE = 100
	_string = type('')

	def __init__(self, fd):
		self.q = Queue.Queue(self.QSIZE)

		def rhelper(fd, q):
			try:
				for l in fd:
					q.put(l)
				q.put(None)
				# while True:
					# l = fd.readline()
					# if l == '':
						# q.put(None)
						# break
					# else:
						# q.put(l)
						
			except (Exception, KeyboardInterrupt):
				q.put( sys.exc_info() )
	
		self.rh = threading.Thread(target=rhelper, args=(fd, self.q))
		self.rh.start()


	def readline(self):
		if self.q is None:
			return ''
		x = self.q.get()
		if type(x) != self._string:
			self.rh.join()
			self.q = None
			if x is not None:
				raise x[0], x[1], x[2]
			return ''
		return x


	def readlines(self):
		o = []
		while self.q is not None:
			x = self.q.get()
			if type(x) != self._string:
				self.rh.join()
				self.q = None
				if x is not None:
					raise x[0], x[1], x[2]
				break
			o.append( x )
		return o


	def read_iter(self):
		while self.q is not None:
			x = self.q.get()
			if type(x) != self._string:
				self.rh.join()
				self.q = None
				if x is not None:
					raise x[0], x[1], x[2]
				break
			yield x

	__iter__ = read_iter


def thr_iter_read(fd):
	"""Read the contents of a file as an iterator.
	The read is two-threaded, so that one thread can be
	waiting on disk I/O while the other thread is
	processing the results.
	"""
	x = threaded_readable_file(fd)
	return x.read_iter()



def makedirs(fname, mode=0775):
	"""This makes the specified directory, including all
	necessary directories above it.    It is like os.makedirs(),
	except that if the directory already exists, it
	does not raise an exception.
	"""
	import os
	try:
		os.makedirs(fname, mode)
	except OSError, x:
		if os.path.isdir(fname) and os.access(fname, os.F_OK):
			return
		raise



def shuffle_Nrep(y, n=1, cmp=None):
	"""Shuffle a list, y,
	so that no item occurs more than n times in a row.
	Equality is determined by the comparison function cmp returning zero.
	"""
	import random
	assert n>0, "Silly!"
	x = y[:]
	random.shuffle(x)
	m = len(x)
	if cmp is None:
		cmp = lambda a, b: a==b

	passes = 0
	restart = 0
	while passes<1000:
		prb = None
		pstart = 0
		reps = 0
		# print 'x=', x
		for i in range(max(1, restart), m):
			if cmp(x[i-1], x[i]):
				reps += 1
				pstart = i - 1
			else:
				pstart = None
				reps = 0
			if reps >= n:
				prb = i
				break
		if prb is None:
			y[:] = x
			return y

		k = prb+1
		found = False
		while k < m:
			if not cmp(x[pstart], x[k]):
				found = True
				break
			k += 1
		if not found:
			# print 'ROLL'
			tmp = x.pop(0)
			x.append(tmp)
			restart = 0
			continue
		a = pstart
		b = k + 1
		# print 'a,b=', a, b
		tmp = x[a:b]
		random.shuffle(tmp)
		# print 'tmp=', x[a:b], '->', tmp
		x[a:b] = tmp
		restart = a
		passes += 1
	raise RuntimeError, 'Too many passes: cannot avoid repetitions'


def testSNR():
	import random
	for i in range(20):
		x = [ i//10 for i in range(20) ]
		shuffle_Nrep(x, 1)
		for i in range(len(x)-1):
			assert x[i] != x[i+1], 'Whoops: i=%d, %d %d' % (i, x[i], x[i+1])
		x = [ i//3 for i in range(10000) ]
		random.shuffle(x)
		shuffle_Nrep(x, 1)
		for i in range(len(x)-1):
			assert x[i] != x[i+1], 'Whoops: i=%d, %d %d' % (i, x[i], x[i+1])


def open_nowipe(nm1, nm2, mode="w"):
	"""Open a file (typically for writing) but make sure that the
	file doesn't already exist.   The name is constructed from
	nm1 a sequence number and nm2.   The sequence number gets incremented
	until a name is found that doesn't exist.
	Typically, nm2 is a suffix like ".wav"
	@param nm1: the part of the name to the left of the sequence number
	@param nm2: the part of the name to the right of the sequence number
	@param mode: The way to open the file -- passed to open().
	@type nm1: str
	@type nm2: str
	@type mode: str
	"""
	i = 0
	try:
		while True:
			nm = '%s%d%s' % (nm1, i, nm2)
			open(nm, 'r')
			i += 1
	except IOError:
		pass
	return (open(nm, mode), nm)


def dropfront(prefix, s):
	"""Drops the prefix from the string and raises an exception
	if it is not there to be dropped.
	"""
	if not s.startswith(prefix):
		raise ValueError, "String '%s' must start with '%s'" % (s[:20], prefix)
	return s[len(prefix):]


def open_compressed(fn):
	import g_pipe

	if fn.endswith('.bz2'):
		ci, co = g_pipe.popen2("bzcat", ['bzcat', fn])
		ci.close()
		return co
	elif fn.endswith('.gz'):
		ci, co = g_pipe.popen2("zcat", ['zcat', fn])
		ci.close()
		return co
	return open(fn, 'r')


def gammaln(x):
    """
Returns the gamma function of xx.
Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
(Adapted from: Numerical Recipies in C. via code
Copyright (c) 1999-2000 Gary Strangman and released under the LGPL.)
"""
    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    tmp = x + 4.5
    tmp -= (x-0.5)*math.log(tmp)
    ser = 1.0
    for cj in coeff:
        ser += cj/x
        x += 1
    return -tmp + math.log(2.50662827465*ser)


def log_t_density(x, nu):
	c = gammaln((nu+1)/2.0) - 0.5*math.log(nu*math.pi) - gammaln(nu/2.0)
	return math.log(1+x**2/nu)*(-(nu+1)/2.0)



_a_factor_cache = {1:1, 2:2, 3:3}	# THIS CACHE SHOULD BE LOCKED
def a_factor(n):	# Don't mess with private_start.
	"""Finds the smallest prime factor of a number."""

	try:
		return _a_factor_cache[n]
	except KeyError:
		pass
	for p in primes():
		if p*p > n:
			f = n
			break
		if n%p == 0:
			f = p
			break
	_a_factor_cache[n] = f
	return f


_primes = [2, 3]	# 2, 3 *must* be there.	# THIS CACHE SHOULD BE LOCKED
def primes():
	"""This is a generator that produces an infinite list of primes.
	"""
	for p in _primes:
		yield p
	i = _primes[-1] + 2
	while True:
		for p in primes():
			if p*p > i:
				if p > _primes[-1]:	# multithreading...
					_primes.append(i)
				yield i
			if i%p == 0:
				i += 2
				break


_factor_cache = {}	# THIS CACHE SHOULD BE LOCKED
def factor(n):	# Don't mess with private_start.
	"""Factor a number into a list of prime factors,
	in increasing order.
	@param n: input number
	@type n: int
	@return: prime factors
	@rtype: list
	"""

	try:
		return _factor_cache[n]
	except KeyError:
		pass
	f = a_factor(n)
	if f == n:
		tmp = [n]
	else:
		tmp = [f] + factor(n//f)
	_factor_cache[n] = tmp[:]
	return tmp


def test_primes():
	assert factor(11) == [11]
	assert factor(16) == [2, 2, 2, 2]
	assert factor(100) == [2, 2, 5, 5]
	assert factor(2) == [2]
	assert factor(97) == [97]
	assert factor(55) == [5, 11]
	assert gcd(5,3)==1
	assert gcd(14, 21)==7
	assert gcd(100, 70)==10

def gcd(a, b):
	"""Greatest common factor/denominator.
	@type a: int
	@type b: int
	@rtype: int
	@return: the greatest common factor of a and b.
	"""
	assert a >= 0 and b >= 0
	while b != 0:
		tmp = b
		b = a % b
		a = tmp
	return a


if __name__ == '__main__':
	testCM()
	testSNR()
	test_primes()
