"""Fit a linear transform to a bunch of
input/output vectors."""


from gmisclib import Num
from gmisclib import gpk_lsq
from gmisclib import gpk_rlsq
from gmisclib import gpkmisc


def err_before_fit(data):
	"""@return: Returns the per-coordinate sum-squared-error
		of the output coordinates. (float).
	@param data: [(input_coordinates, output_coordinates), ...].
		A list of (in,out) tuples corresponding to the
		independent and dependent parameters of the linear transform.
		Both C{in} and C{out} are one-dimensional
		L{numpy vectors<numpy.ndarray>).   They don't need to have
		the same length, though (obviously) all instances of "in"
		need to have the same length and all instances of "out"
		also need to match one another.
	@type data: [(L{numpy.ndarray}, L{numpy.ndarray}), ...]
	"""

	if len(data) < 2:
		return None

	m = None
	o = []
	for (ic, oc) in data:
		assert len(oc.shape) == 1, "Dependent data array must be 1-dimensional, not %d" %  len(oc.shape)
		if m is None:
			m = oc.shape[0]
		assert m == oc.shape[0], "Bad output size: %d vs. previous %d" % (oc.shape[0], m)
		o.append(oc)
	sum = Num.zeros((m,), Num.Float)
	for tmp in o:
		Num.add(sum, tmp, sum)
	avg = sum/len(o)
	sumsq = Num.zeros((m,), Num.Float)
	for tmp in o:
		Num.add(sumsq, (tmp - avg)**2, sumsq)
	return sumsq


# def _pack(data):
	# # Build the data array:
	# # Build the array of basis functions:
	# # M will be the number of output coordinates (data points).
	# m = None
	# # N will be the number of input coordinates (parameters).
	# n = None
	# o = []
	# i = []
	# for (ic, oc) in data:
		# assert len(oc.shape) == 1, "Dependent data array must be 1-dimensional, not %d" % len(oc.shape)
		# assert len(ic.shape) == 1, "Independent data array must be 1-dimensional, not %d" % len(ic.shape)
		# if m is None:
			# m = oc.shape[0]
		# assert m == oc.shape[0], "Bad output size: %d vs. previous %d" % (oc.shape[0], m)
		# if n is None:
			# n = ic.shape[0]
		# assert n == ic.shape[0], "Bad input size: %d vs. previous %d" % (ic.shape[0], m)
		# # Pack into matrices
		# o.append(oc)
		# i.append(Num.concatenate( ([1.0], ic) ) )
	# return (Num.array(i), Num.array(o), m, n)


def _pack(data, constant=True):
	# Build the data array:
	# Build the array of basis functions:
	ic, oc = data[0]
	# M will be the number of output coordinates (data points).
	# N will be the number of input coordinates (parameters).
	m = oc.shape[0]
	n = ic.shape[0]
	c = int(constant)
	nd = len(data)
	i = Num.zeros((nd, n+c), Num.Float)
	o = Num.zeros((nd, m), Num.Float)
	for (j,(ic, oc)) in enumerate(data):
		o[j,:] = oc
		if constant:
			i[j,0] = 1.0
			i[j,1:] = ic
		else:
			i[j,:] = ic
	return (i, o, m, n)




# This is used to compute the matrix of derivitives,
# which is then used to compute the step in mcmcSQ.py
def localfit(data, minsv=None, minsvr=None):
	"""Does a linear fit to data via a singular value decomposition
	algorithm.
	It returns the matrix A and vector B such that
	C{A*input_coordinates+B} is the best fit to C{output_coordinates}.
	@param minsv: sets the minimum useable singular value;
	@param minsvr: sets the minimum useable s.v. in terms of the largest s.v.
	@type minsv: float or None
	@type minsvr: float or None
	@return: (A, B, errs, sv, ranks) where
		- A is a 2-D L{numpy.ndarray} matrix.
		- B is a 1-D L{numpy.ndarray} vector.
		- errs is a vector, one value for each output coordinate.
		- sv are the singular values, sorted into decreasing order.
	@param data: [(input_coordinates, output_coordinates), ...].
		A list of (in,out) tuples corresponding to the
		independent and dependent parameters of the linear transform.
		Both C{in} and C{out} are one-dimensional
		L{numpy vectors<numpy.ndarray>).   They don't need to have
		the same length, though (obviously) all instances of "in"
		need to have the same length and all instances of "out"
		also need to match one another.
	@type data: [(L{numpy.ndarray}, L{numpy.ndarray}), ...]
	"""

	ii, oo, m, n = _pack(data)
	data = None	# Reclaim memory
	soln = gpk_lsq.linear_least_squares(ii, oo, minsv=minsv, minsvr=minsvr)
	ii = None	# Free unneeded memory.
	oo = None	# Free unneeded memory.
	errs = Num.sum( soln.residual()**2, axis=0 )
	sv = soln.sv()
	x = soln.x()
	rank = soln.rank()
	assert sv.shape[0]>=rank and sv.shape[0]<=n+1, "sv.shape=%s rank=%d m=%d n=%d" % (str(sv.shape), rank, m, n)
	assert rank <= 1+n
	assert len(errs) == m
	assert len(soln.x().shape) == 2
	return ( Num.transpose(x[1:,:]), x[0,:],
			errs, Num.sort(sv)[::-1], rank
			)


# This is used to compute the matrix of derivitives,
# which is then used to compute the step in mcmcSQ.py
def r_localfit(data, minsv=None, minsvr=None):
	"""Data is [ (input_coordinates, output_coordinates), ... ]
	Minsv sets the minimum useable singular value;
	minsvr sets the minimum useable s.v. in terms of the largest s.v..
	It returns the matrix A and vector B such that the best fit
	is A*input_coordinates+B in a tuple
	(A, B, errs, sv, ranks).
	errs is a vector, one value for each output coordinate.
	sv is sorted into decreasing order -- it's a bit of a fake.
	Rank is the minimum rank of the various fits.
	"""

	ii, oo, m, n = _pack(data)
	data = None	# Reclaim memory
	errs = []
	rank = None
	sv = []
	const = Num.zeros((m,), Num.Float)
	coef = Num.zeros((n,m), Num.Float)
	for j in range(m):
		assert oo.shape[1] == m
		soln = gpk_rlsq.robust_linear_fit(ii, oo[:,j], 1, minsv=minsv, minsvr=minsvr)
		errs.append( Num.sum( soln.residual()**2 ) )
		if rank is None or rank > soln.rank():
			rank = soln.rank()
		svtmp = soln.sv()
		sv.append( svtmp )
		const[j] = soln.x()[0]
		coef[:,j] = soln.x()[1:]
	ii = None	# Free unneeded memory.
	oo = None	# Free unneeded memory.
	sv = Num.array(sv)
	# print 'svshape=', sv.shape, m
	assert sv.shape[0] == m
	svs0 = sv.shape[1]
	sv = gpkmisc.N_median_across(sv)
	assert sv.shape[0] == svs0
	assert sv.shape[0] >= rank and sv.shape[0] <= n+1, "sv.shape=%s rank=%d m=%d n=%d" % (str(sv.shape), rank, m, n)
	assert rank <= 1+n
	assert len(errs) == m
	return ( Num.transpose(coef), const, errs, Num.sort(sv)[::-1], rank)


def leaktest():
	import RandomArray
	while 1:
		d = []
		for i in range(100):
			d.append( (RandomArray.standard_normal((30,)),
					RandomArray.standard_normal((1000,))))
		localfit(d)

def test_localfit11(r):
	d = [	(Num.array((0,)), Num.array((-1,))),
		(Num.array((1,)), Num.array((0,))),
		(Num.array((2,)), Num.array((1+1e-7,))),
		(Num.array((3,)), Num.array((2,))),
		]
	if r:
		coef, const, errs, sv, rank = r_localfit(d)
	else:
		coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert coef.shape == (1,1)
	assert abs(coef[0,0]-1) < 1e-6
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 2
	assert rank == 2
	assert Num.alltrue(err_before_fit(d) >= errs)


def test_localfit21():
	d = [ (Num.array((0,0)), Num.array((-1,))),
		(Num.array((1,2)), Num.array((0,))),
		(Num.array((2,-1)), Num.array((1,))) ]
	coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert coef.shape == (1,2)
	assert Num.sum(Num.absolute(coef-[[1,0]])) < 1e-6
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 3
	assert rank == 3
	assert Num.alltrue(err_before_fit(d) >= errs)

def test_localfit21u():
	d = [ (Num.array((0,0)), Num.array((-1,))),
		(Num.array((2,-1)), Num.array((1,))) ]
	coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert abs(const[0] + 2*coef[0,0]-coef[0,1] - 1) < 1e-6
	assert coef.shape == (1,2)
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 2
	assert rank == 2
	assert Num.alltrue(err_before_fit(d) >= errs)

def test_localfit22(r):
	d = [ (Num.array((0,0)), Num.array((-1,0))),
		(Num.array((1,2)), Num.array((0,1.0))),
		(Num.array((-1,2)), Num.array((-2,1.0))),
		(Num.array((-1,1)), Num.array((-2+1e-7,0.5+1e-7))),
		(Num.array((2,-1)), Num.array((1,-0.5))) ]

	if r:
		coef, const, errs, sv, rank = r_localfit(d)
	else:
		coef, const, errs, sv, rank = localfit(d)

	print const
	print coef
	print  errs
	print  sv
	print rank
	assert const.shape == (2,)
	assert Num.sum(Num.absolute(const - [-1,0])) < 1e-6
	assert coef.shape == (2,2)
	assert Num.sum(Num.absolute(coef[0]-[1,0])) < 1e-6
	assert Num.sum(Num.absolute(coef[1]-[0,0.5])) < 1e-6
	assert len(errs)==2
	assert Num.sum(errs) < 1e-6
	assert len(sv) == 3
	assert rank == 3
	assert Num.alltrue(err_before_fit(d) >= errs)

if __name__ == '__main__':
	test_localfit11(False)
	test_localfit21()
	test_localfit21u()
	for r in [False, True]:
		test_localfit11(r)
		test_localfit22(r)
