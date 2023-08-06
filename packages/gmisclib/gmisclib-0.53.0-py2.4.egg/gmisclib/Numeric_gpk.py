
import Num as N
import math


def add_overlap(a, astart, b, bstart):
	"""Add arrays a and b in the overlap region.
	Return (data, start).
	If a, b are time series, they are assumed to have the
	same sampling rate.
	Astart and Bstart apply to the zeroth index.
	All other indices are assumed to match start and length.
	"""
	start = max(astart, bstart)
	end = min(astart+a.shape[0], bstart+b.shape[0])

	out = a[start-astart:end-astart] + b[start-bstart:end-bstart]

	return (out, start)




# def asinh(x):
        # sign = N.sign(x)
	# return sign*N.log(sign*x + N.sqrt(x*x + 1))
asinh = N.arcsinh

# def acosh(x):
	# assert N.all(N.less_equal(x, 1))
	# return N.log(x - N.sqrt(x*x-1))
acosh = N.arccosh


def zero_pad_end(d, padfactor=1):
	if padfactor == 0:
		return N.array(d, copy=1)
	elif padfactor<=0:
		raise ValueError, 'pad factor <= 0'
	assert len(d.shape) == 1
	n = d.shape[0]
	npad = int(round(n*padfactor))
	return N.concatenate( (d, N.zeros((npad,),  N.Float)) )


def Poisson(nbar):
	"""Return a Poisson random integer, whose distribution has
	a mean = nbar.
	"""
	import random
	assert nbar >= 0.0
	if nbar < 20.0:
		L = math.exp(-nbar)
		k = -1
		p = 1.0
		while p >= L:
			k += 1
			p *= random.random()
	else:
		lp = 0.0
		lL = -nbar
		k = 0
		chunk = min( int(round (1 + nbar + 3*math.sqrt(nbar) )), 10000)
		while lp >= lL:
			ptmp = N.log(N.RA.uniform(0.0, 1.0, chunk) )
			lpp = N.add.accumulate(ptmp) + lp
			fsm = N.nonzero(N.less(lpp, lL))[0]
			if fsm.shape[0] != 0:
				k += fsm[0]
				break
			k += ptmp.shape[0]
			lp = lpp[-1]
	return k



def _test_Poisson():
	Nbar = 0.01
	N = int(round(1000/Nbar))
	s = 0
	for i in range(N):
		s += Poisson(Nbar)
	assert abs(s-N*Nbar) < 5*math.sqrt(N*Nbar)


	Nbar = 25.0
	N = 1000
	s = 0
	for i in range(N):
		s += Poisson(Nbar)
	assert abs(s-N*Nbar) < 5*math.sqrt(N*Nbar)



def bevel_concat(a, b, bevel=0, bevel_overlap=1.0, delay=0,
			ta=None, tb=None):
	"""Concatenate two time series.  Bevel the edges,
	and overlap them slightly.

	Bevel_overlap controls the fractional overlap of the two bevels,
	and delay specifies an extra delay for b.

	If ta and/or tb are specified, return a tuple of
	(concatenated_time_series, tma, tmb) where tma and tmb are the locations
	corresponding to ta and tb in the corresponding input arrays.
	"""
	assert bevel >= 0
	if bevel > 0:
		bev = (0.5 + N.arrayrange(bevel))/float(bevel)
	else:
		bev = 1
	bc = N.array(b, copy=True)
	bev = (0.5 + N.arrayrange(bevel))/float(bevel)
	ans = a.shape[0]-1
	bns = bc.shape[0]-1
	bos = a.shape[0] - int(round(bevel_overlap*bevel)) + delay
	boe = bos + bc.shape[0]
	o = N.zeros((boe,), N.Float)
	o[:a.shape[0]] = a
	if bevel > 0:
		N.multiply(o[:bevel], bev, o[:bevel])
		N.multiply(o[ans:ans-bevel:-1], bev, o[ans:ans-bevel:-1])
		N.multiply(bc[:bevel], bev, bc[:bevel])
		N.multiply(bc[bns:bns-bevel:-1], bev, bc[bns:bns-bevel:-1])
	N.add(o[bos:boe], bc, o[bos:boe])
	if ta is not None or tb is not None:
		if tb is not None:
			tb += bos
		return (o, ta, tb)
	else:
		return o


def argmax(a):
	i = N.argmax(a, axis=None)
	o = []
	for n in reversed(a.shape):
		o.append( i % n )
		i = i//n
	o.reverse()
	return tuple(o)


def _test_argmax():
	x = N.array([1,2,3,4,3])
	assert argmax(x) == (3,)
	x = N.array([[1,2,3,4,3], [0,1,0,1,0]])
	assert x[argmax(x)] == 4
	x = N.array([[1,2,3,4,3], [0,1,0,5,0]])
	assert x[argmax(x)] == 5
	x = N.array([[1,2], [3,4], [5,6], [0,1],[0,5],[0,7]])
	assert x[argmax(x)] == 7
	x = N.zeros((5,4,3,3,1,2), N.Float)
	x[2,1,0,1,0,1] = 100.0
	assert argmax(x) == (2,1,0,1,0,1)
	x[0,0,0,0,0,0] = 200.0
	assert argmax(x) == (0,0,0,0,0,0)
	x[4,3,2,2,0,1] = 300.0
	assert argmax(x) == (4,3,2,2,0,1)
	x[4,3,2,2,0,0] = 400.0
	assert argmax(x) == (4,3,2,2,0,0)
	x[4,3,2,0,0,0] = 500.0
	assert argmax(x) == (4,3,2,0,0,0)


def N_maximum(a):
	assert len(a.shape) == 1
	return a[N.argmax(a)].item()


def N_minimum(a):
	assert len(a.shape) == 1
	return a[N.argmin(a)].item()


# Median along the first axis.
N_median = N.median


def N_frac_rank(a, fr):
	assert 0 <= fr <= 1.0
	tmp = N.sort(a)
	n = tmp.shape[0]
	assert n > 0, "Zero-sized array: cannot compute rank."
	return tmp[int(round((n-1)*fr))].item()


def N_mean_ad(a):
	"""Mean absolute deviation.   For a multi-dimensional array,
	it takes the MAD along the first axis, so
	N_mean_ad(x)[0]==N_mean_ad(x[:,0]).
	"""
	ctr = N.median(a)
	diff = N.subtract(a, ctr)
	return N.sum(N.absolute(diff), axis=0)/(diff.shape[0]-1)


def _test_N_mean_ad():
	x = N.zeros((2,1), N.Float)
	x[0,0] = 1
	x[1,0] = 0
	assert N.allclose(N_mean_ad(x), [1.0])
	x = N.zeros((5,7), N.Float)
	x[0,0] = 1
	y = N_mean_ad(x)
	assert y.shape == (7,)
	assert N.allclose(y, [(1.0-0.0)/4.0, 0, 0, 0, 0, 0, 0])
	assert abs(N_mean_ad(x)[0]-N_mean_ad(x[:,0])) < 0.001


def median_across(list_of_vec):
	"""Returns an element-by-element median of a list of Numeric vectors."""
	assert len(list_of_vec[0].shape) == 1
	o = N.zeros(list_of_vec[0].shape, N.Float)
	tmp = N.zeros((len(list_of_vec),), N.Float)
	for t in list_of_vec:
		assert t.shape == o.shape
	for i in range(o.shape[0]):
		for (j, v) in enumerate(list_of_vec):
			tmp[j] = v[i]
		o[i] = N_median(tmp)
	return o



if hasattr(N, 'var'):
	variance = N.var
else:
	def variance(x):
		BLOCKSIZE = 20000
		x = N.asarray(x, N.Float)
		n = x.shape[0]
		x0 = x[0]
		s = 0.0
		ss = 0.0
		for i in range(0, x.shape[0], BLOCKSIZE):
			e = min(n, i+BLOCKSIZE)
			tmp = x[i:e] - x0
			s += N.sum(tmp, axis=0)
			ss += N.sum(tmp**2, axis=0)
		return N.maximum(ss-s**2/n, 0.0)/(n-1)


if hasattr(N, 'std'):
	stdev = N.std
else:
	def stdev(x):
		return math.sqrt(variance(x))


if hasattr(N, 'diag'):
	make_diag = N.diag
else:
	def make_diag(x):
		"""Construct a square diagonal matrix whose elements
		are taken from the vector x.
		"""
		x = N.asarray(x, N.Float)
		assert len(x.shape) == 1
		n = x.shape[0]
		o = N.zeros((n,n), N.Float)
		for i in range(n):
			o[i,i] = x[i]
		return o


def set_diag(x, a):
	"""Set the diagonal of a matrix x to be the vector a.
	If a is shorter than the diagonal of x, just set the beginning."""

	assert len(a.shape) == 1
	assert len(x.shape) == 2
	n = a.shape[0]
	assert x.shape[0] >= n
	assert x.shape[1] >= n
	for i in range(n):
		x[i,i] = a[i]


# Take the median along the first coordinate of a 2-D matrix,
# so if m.shape=(2,4) then the output will have shape (4,)
N_median_across = N.median


def _test_N_median_across():
	x = N.zeros((3,2), N.Float)
	x[0,0] = 1
	x[1,0] = 2
	x[2,0] = 3
	y = N_median_across(x)
	assert N.allclose(y, [2.0, 0.0])


if hasattr(N, 'clip'):
	def limit(low, x, high):
		return N.clip(x, low, high)
else:
	def limit(low, x, high):
		"""Force x to be in the range [low, high]."""
		assert high >= low, "Impossible limit: high=%s is not >= low=%s." % (str(high), str(low))
		if x < low:
			return low
		if x > high:
			return high
		return x



def trimmed_mean_sigma_across(list_of_vec, weights, clip):
	import gpkavg
	"""Returns an element-by-element trimmed_mean of a list of Numeric vectors.
	For instance, the first component of the output vector is the trimmed mean
	of the first component of all of the input vectors.
	"""
	import gpkavg
	assert len(list_of_vec[0].shape) == 1
	om = N.zeros(list_of_vec[0].shape, N.Float)
	osig = N.zeros(list_of_vec[0].shape, N.Float)
	tmp = N.zeros((len(list_of_vec),), N.Float)
	for t in list_of_vec:
		assert t.shape == om.shape
	for i in range(om.shape[0]):
		for (j, v) in enumerate(list_of_vec):
			tmp[j] = v[i]
		om[i], osig[i] = gpkavg.avg(tmp, weights, clip)
	return (om, osig)

def trimmed_mean_across(list_of_vec, weights, clip):
	return trimmed_mean_sigma_across(list_of_vec, weights, clip)[0]

def trimmed_stdev_across(list_of_vec, weights, clip):
	return trimmed_mean_sigma_across(list_of_vec, weights, clip)[1]


def vec_variance(x):
	"""Take a component-by-component variance of a list of vectors."""
	n = len(x)
	if n < 2:
		raise ValueError, "Cannot take variance unless len(x)>1"
	x0 = x[0]
	sh = x0.shape
	s = N.zeros(sh, N.Float)
	ss = N.zeros(sh, N.Float)
	for xi in x:
		assert xi.shape == sh
		tmp = xi - x0
		N.add(s, tmp, s)
		N.add(ss, tmp**2, ss)
	return N.maximum(ss-s**2/n, 0.0)/(n-1)




def qform(vec, mat):
	"""A quadratic form: vec*mat*vec,
	or vecs*mat*transpose(vecs)"""
	if len(vec.shape) != 1 or len(mat.shape) != 2:
		raise ValueError, ': '.join(["Can't handle input",
					     "requires vector*matrix(vector)",
					     "shapes are %s and %s" % (
							vec.shape, mat.shape)
						])
	if mat.shape != (vec.shape[0], vec.shape[0]):
		raise ValueError, ': '.join([
					"Matrix must be square and match the length of vector",
					"shapes are %s and %s" % (vec.shape, mat.shape)
					])
	return N.dot(vec, N.matrixmultiply(mat, vec))



def KolmogorovSmirnov(d1, d2, w1=None, w2=None):
	d1 = N.asarray(d1)
	d2 = N.asarray(d2)
	assert len(d1.shape) == 1, 'd1.shape=%s' % str(d1.shape)
	assert len(d2.shape) == 1, 'd2.shape=%s' % str(d2.shape)
	if w1 is None:
		w1 = N.ones(d1.shape, N.Float)
	if w2 is None:
		w2 = N.ones(d2.shape, N.Float)
	ws1 = N.sum(w1)
	ws2 = N.sum(w2)
	i1 = N.argsort(d1)
	i2 = N.argsort(d2)
	c1 = 0.0
	c2 = 0.0
	j1 = 0
	j2 = 0
	maxdiff = 0.0
	while True:
		if abs(c1-c2) > maxdiff:
			maxdiff = abs(c1 - c2)
		if j1 < i1.shape[0]-1 and j2<i2.shape[0]-1:
			if d1[i1[j1]] < d2[i2[j2]]:
				j1 += 1
				c1 += w1[i1[j1]]/ws1
			elif d1[i1[j1]] > d2[i2[j2]]:
				j2 += 1
				c2 += w2[i2[j2]]/ws2
			else:
				j1 += 1
				c1 += w1[i1[j1]]/ws1
				j2 += 1
				c2 += w2[i2[j2]]/ws2
		elif j1==i1.shape[0]-1 and j2==i2.shape[0]-1:
			break
		elif j1 < i1.shape[0]-1:
			j1 += 1
			c1 += w1[i1[j1]]/ws1
		else:
			j2 += 1
			c2 += w2[i2[j2]]/ws2
	return maxdiff


def _testKS():
	assert KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3.01, 3, 4, 5]) < 0.001
	assert abs( KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3, 4, 5, 6]) - 0.16667) < 0.001
	print KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3, 4, 5])




def interpN(a, t):
	"""Interpolate array a to floating point indices, t,
	via nearest-neighbor interpolation.
	Returns a Numeric array.
	"""
	ii = N.around(t)
	n = a.shape[0]
	if not N.alltrue((ii>=0) * (ii<=n-1)):
		raise IndexError, "Index out of range."
	iii = ii.astype(N.Int)
	return N.take(a, iii, axis=0)



def interp(a, t):
	"""Interpolate to a specified time axis.
	This does a linear interpolation.
	A is a Numpy array, and t is an array of times.
	Returns a Numpy array.
	"""
	n = a.shape[0]
	nt = t.shape[0]
	las = len(a.shape)
	# print 'a=', a.shape, a
	if las == 1:
		# print 'a.shape=', a.shape
		a = N.transpose([a], N.Float)
	m = a.shape[1]
	ii = N.around(t)
	assert ii.shape == t.shape

	# print 't=', t
	# print 'n=', n, 'ii=', ii
	if not N.alltrue((ii>=0) * (ii<=n-1)):
		raise IndexError, "Index out of range."

	nearestT = ii.astype(N.Int)
	assert nearestT.shape == t.shape

	nearestA = N.take(a, nearestT, axis=0)
	assert nearestA.shape == (nt,m)
	deltaT = t - nearestT
	assert deltaT.shape == nearestT.shape
	isupport = N.where((deltaT>=0)*(nearestT<n-1)+(nearestT<=0), 1, -1) + nearestT
	assert isupport.shape == (nearestA.shape[0],)
	assert isupport.shape == nearestT.shape
	assert isupport.shape == deltaT.shape
	# print 'a=',a 
	# print 'isupport=', isupport
	support = N.take(a, isupport, axis=0)
	assert support.shape == (nt,m)
	if len(a.shape) > 1:
		assert nearestA.shape == (nt,m)
		deltaA = (deltaT/(isupport-nearestT))[:,N.NewAxis] * (support-nearestA)
		assert deltaA.shape[1] == a.shape[1]
	else:
		deltaA = (deltaT/(isupport-nearestT)) * (support-nearestA)
	assert deltaA.shape == nearestA.shape
	rv = nearestA + deltaA
	if las == 1:
		return rv[:,0]
	return rv


def _test_interp1():
	a = N.array([[1.0], [2.0]])
	# a = N.array([1.0, 2.0], N.Float)
	t = N.array([0.5])
	q = interp(a, t)
	assert q.shape == (1,1)
	assert N.sum(N.absolute(interp(a, t) - [1.5])) < 1e-3


def split_into_clumps(x, threshold, minsize=1):
	"""This reports when the signal is above the threshold.
	@param x: a signal
	@type x: L{numpy.ndarray}, one-dimensional.
	@param threshold: a threshold.
	@type threshold: float
	@returns: [(start, stop), ...] for each region ("clump") where C{x>threshold}.
	"""
	assert len(x.shape) == 1
	gt = N.greater(x, threshold)
	chg = gt[1:] - gt[:-1]
	nz = N.nonzero(chg)[0]
	rv = []
	if gt[0]:
		last = 0
	else:
		last = None
	for i in nz:
		if last is None:
			last = i+1
		else:
			if minsize > 0:
				rv.append( (last, i+1) )
			last = None
	if last is not None and gt.shape[0]>=last+minsize:
		rv.append( (last, gt.shape[0]) )
	return rv


def _test_split_into_clumps():
	tmp = split_into_clumps(N.array([0,0,0,1,0,0]), 0.5)
	assert tmp == [(3,4)]
	tmp = split_into_clumps(N.array([1,0,0]), 0.5)
	assert tmp == [(0,1)]
	tmp = split_into_clumps(N.array([0,0,0,1]), 0.5)
	assert tmp == [(3,4)]
	tmp = split_into_clumps(N.array([1]), 0.5)
	assert tmp == [(0,1)]
	tmp = split_into_clumps(N.array([0]), 0.5)
	assert tmp == []
	tmp = split_into_clumps(N.array([1]), 0.5, minsize=2)
	assert tmp == []
	tmp = split_into_clumps(N.array([0,0,0,1,1,0]), 0.5, minsize=2)
	assert tmp == [(3,5)]


if __name__ == '__main__':
	_test_split_into_clumps()
	_test_argmax()
	_test_interp1()
	_test_Poisson()
	_test_N_mean_ad()
	_test_N_median_across()
