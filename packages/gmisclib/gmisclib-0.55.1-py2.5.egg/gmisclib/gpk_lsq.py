from gmisclib import Num
import gmisclib.Numeric_gpk as NG

class lls_base(object):
	def __init__(self, a, copy=True):
		self.ginv = None
		self._fit = None
		self._x = None
		self._hatdiag = None
		self._y = None
		self.a = Num.array(a, Num.Float, copy=copy)
		if len(self.a.shape) != 2:
			raise ValueError, "a needs to be 2-dimensional: shape=%s" % str(self.a.shape)
		self.m, self.n = self.a.shape
		self.q = None


	def set_y(self, y, copy=True):
		if y is None:
			return
		self._fit = None
		self._x = None
		self._y = Num.array(y, Num.Float, copy=copy)
		if len(self._y.shape) == 1:	# Vector
			self.vector = True
			self._y = Num.transpose( [y] )
		elif len(self._y.shape) > 2:
			raise ValueError, "y needs to be 1- or 2-dimensional: shape=%s" % str(self._y.shape)
		else:
			self.vector = False
		if self._y.shape[0] != self.m:
			raise ValueError, "Matrix sizes do not match: (%d,%d) and %s" % (
								self.m, self.n, str(self._y.shape)
								)
		self.q = self._y.shape[1]


	def y(self, copy=True):
		if self.vector:
			return Num.array(self._y[:,0], copy=copy)
		return Num.array(self._y, copy=copy)


	def _solve(self):
		raise RuntimeError, "Virtual Function"


	def hat(self, copy=True):
		raise RuntimeError, "Virtual Function"


	def x(self, y=None, copy=True):
		self.set_y(y)
		assert self._y is not None, "Y not yet set"
		if self._x is None:
			self._x = self._solve()
			if self.vector:	# Restore everything to vectors
				self._x = self._x[:, 0]
		return Num.array(self._x, copy=copy)


	def fit(self, copy=False):
		if self._fit is None:
			self._fit = Num.dot(self.a, self.x(copy=False))
		return Num.array(self._fit, copy=copy)


	def residual(self):
		# print 'resid shapes=', self.fit().shape, self._y.shape
		return self.y() - self.fit()


	def variance_about_fit(self):
		"""Returns the estimator of the standard deviation
		of the data about the fit.
		@return: L{numpy.ndarray} with shape=(q,).   Each entry corresponds
			to one of the C{q} sets of equations that are being fit.
		"""
		r2 = Num.sum(self.residual()**2, axis=0)
		assert self.vector and r2.shape==() or not self.vector and r2.shape==(self.q,)
		return r2/(self.m-self.n)


	def eff_rank(self):
		return Num.sum(1.0 - self.hat(copy=False))



class linear_least_squares(lls_base):
	def __init__(self, a, y=None, minsv=None, minsvr=None, copy=True):
		"""This solves the set of linear equations a*x = y,
		and returns (x, the_fit, rank, s).
		Normally, a.shape==(m,n) and y.shape==(m,q),
		and the returned x.shape==(n,q).
		where m is the number of constraints provided by the data,
		n is the number of parameters to use in a fit
		(equivalently, the number of basis functions),
		and q is the number of separate sets of equations
		that you are fitting.
		Then, x has shape (n,q) and the_fit has shape (m,q).
		Interpreting this as a linear regression, there are n
		parameters in the model, and m measurements.
		Q is the number of times you apply the model to a
		different data set; each on yields a different solution.
	
		The procedure uses a singular value decomposition algorithm,
		and treats all singular values that are smaller than minsv
		as zero (i.e. drops them). 
		If minsvr is specified, it treates all singular values that
		are smaller than minsvr times the largest s.v. as zero.
		The returned rank is the
		rank of the solution, which is normally the number of
		nonzero elements in x.
		Note that the shape of the solution vector or matrix
		is defined by a and y, and the rank can be smaller
		than m.
	
		Y may be a 1-D matrix (a vector), in which case
		the fit is a vector.    This is the normal
		case where you are fitting one equation.
		If y is a 2-D matrix,
		each column (second index) in y is a separate fit, and
		each column in the solution is a separate result.
		"""
	
		lls_base.__init__(self, a, copy=copy)
		self.set_y(y, copy=copy)

		assert minsv is None or minsv >= 0.0
		assert minsvr is None or 0.0 <= minsvr <= 1.0
		r = min(self.m, self.n)
		u, self.s, vh = Num.LA.svd(self.a)
		assert u.shape == (self.m, self.m)
		assert vh.shape == (self.n, self.n)
		assert self.s.shape == (r,)
		# rbasis = Num.dot(Num.dot(u, sigma), vh)
		# rbasis = Num.dot(u[:,:r]*self.s, vh[:r])
		# rbasis = Num.dot(u[:,:r], self.s*vh)
		# print 'rbasis=', rbasis
		# assert Num.sum(Num.ravel(rbasis-a)**2) < 0.0001*Num.sum(Num.ravel(self.a)**2)
		if minsv is not None and minsvr is not None:
			svrls = max(minsv, minsvr*self.s[Num.argmax(self.s)] )
		elif minsv is not None:
			svrls = minsv
		elif minsvr is not None:
			svrls = minsvr * self.s[Num.argmax(self.s)]
		else:
			svrls = 0.0
	
		self.sim = Num.greater(self.s, svrls)
		isi = Num.where(self.sim, 1.0/Num.where(self.sim, self.s, 1.0), 0.0)
		self.ginv = Num.transpose(Num.dot(u[:,:r]*isi, vh[:r]))

	def _solve(self):
		return Num.dot(self.ginv, self._y)

	def sv(self):
		return self.s

	def rank(self):
		return Num.sum(self.sim)

	def hat(self, copy=True):
		"""Hat Matrix Diagonal
		Data points that are far from the centroid of the X-space are potentially influential.
		A measure of the distance between a data point, xi,
		and the centroid of the X-space is the data point's associated diagonal
		element hi in the hat matrix. Belsley, Kuh, and Welsch (1980) propose a cutoff of
		2 p/n for the diagonal elements of the hat matrix, where n is the number
		of observations used to fit the model, and p is the number of parameters in the model.
		Observations with hi values above this cutoff should be investigated.
		For linear models, the hat matrix

		C{H = X inv(X'X) X'}

		can be used as a projection matrix.
		The hat matrix diagonal variable contains the diagonal elements
		of the hat matrix

		C{hi = xi inv(X'X) xi'}
		"""
		if self._hatdiag is None:
			aainv = Num.dot(self.ginv, Num.transpose(self.ginv))
			hatdiag = Num.zeros((self.a.shape[0],), Num.Float)
			for i in range(hatdiag.shape[0]):
				hatdiag[i] = NG.qform(self.a[i,:], aainv)
				assert -0.001 < hatdiag[i] < 1.001
			self._hatdiag = hatdiag
		return Num.array(self._hatdiag, copy=copy)


	def x_variances(self, copy=True):
		"""Estimated standard deviations of the solution.
		This is the diagonal of the solution covariance matrix.
		"""
		aainv = Num.dot(self.ginv, Num.transpose(self.ginv))
		vaf = self.variance_about_fit()
		rv = Num.outerproduct(aainv.diagonal(), vaf)
		assert rv.shape == self._x.shape
		assert rv.shape == (self.n, self.q)
		if self.vector:
			return rv[0,:]
		return rv




class reg_linear_least_squares(lls_base):
	def __init__(self, a, y, regstr=0.0, regtgt=0.0, rscale=None):
		"""This solves min! |a*x - y|^2 + |regstr*(x-regtgt)|^2,
		and returns (x, the_fit, rank, s).
		Normally, a.shape==(m,n) and y.shape==(m,q),
		where m is the number of data to be fit,
		n is the number of parameters to use in a fit
		(equivalently, the number of basis functions),
		and q is the number of separate sets of equations
		that you are fitting.
		Then, x has shape (n,q) and the_fit has shape (m,q).
	
		The regularization target,
		regtgt is the same shape as x, that is (n,q).
		(It must be a vector if and only if y is a vector.)
		Regstr, the strength of the regularization is
		normally an (n,n) matrix, though (*,n) will work,
		as will a scalar.
	
		Y may be a 1-D matrix (a vector), in which case
		the fit is a vector.    This is the normal
		case where you are fitting one equation.
		If y is a 2-D matrix,
		each column (second index) in y is a separate fit, and
		each column in the solution is a separate result.
		"""
		lls_base.__init__(self, a)
		self.set_y(y)

		if self.vector:
			if len(regtgt.shape) != 1:
				raise ValueError, "regtgt must be a vector if y is a vector."
			regtgt = Num.transpose( [regtgt] )
		self.regtgt = Num.array(regtgt, Num.Float, copy=True)
		if self.regtgt.shape[0] != self.n:
			raise ValueError, "Regtgt shape must match the shape of a"
		regstr = Num.asarray(regstr, Num.Float)
		assert len(regstr.shape) == 2
		assert regstr.shape[1] == self.n
	
		self.rr = Num.dot(Num.transpose(regstr), regstr)
		self.aa = Num.dot(Num.transpose(self.a), self.a)
		if rscale is None:
			self.scale = 1.0
		else:
			self.scale = rscale * Num.trace(self.aa)/Num.trace(self.rr)
		# print 'aa=', self.aa
		# print 'rr=', self.rr
		# print 'traa', Num.trace(self.aa)
		# print 'trrr', Num.trace(self.rr)
		# print 'scale=', self.scale
		self.aareg = self.aa + self.rr*self.scale


	def _solve(self):
		ayreg = Num.dot(Num.transpose(self.a), self._y)	\
				+ Num.dot(self.rr, self.regtgt)*self.scale
		return Num.LA.solve(self.aareg, ayreg)
	

	def sv_reg(self):
		"""Singular values of the regularized problem."""
		return Num.sqrt(Num.LA.eigvalsh(self.aareg))

	def sv_unreg(self):
		"""Singular values of the unregularized problem."""
		return Num.sqrt(Num.LA.eigvalsh(self.aa))

	def hat(self, copy=True):
		"""Hat Matrix Diagonal
		Data points that are far from the centroid of the X-space are potentially influential.
		A measure of the distance between a data point, xi,
		and the centroid of the X-space is the data point's associated diagonal
		element hi in the hat matrix. Belsley, Kuh, and Welsch (1980) propose a cutoff of
		2 p/n for the diagonal elements of the hat matrix, where n is the number
		of observations used to fit the model, and p is the number of parameters in the model.
		Observations with hi values above this cutoff should be investigated.
		For linear models, the hat matrix

		    H = X (X'X)-1 X' 

		    can be used as a projection matrix.
		    The hat matrix diagonal variable contains the diagonal elements
		    of the hat matrix

		        hi = xi (X'X)-1 xi' 
		"""
		if self._hatdiag is None:
			hatdiag = Num.zeros((self.aa.shape[0],), Num.Float)
			iaareg = Num.LA.inv(self.aareg)
			for i in range(hatdiag.shape[0]):
				hatdiag[i] = NG.qform(self.a[i,:], iaareg)
				assert -0.001 < hatdiag[i] < 1.001
			self._hatdiag = hatdiag
		return Num.array(self._hatdiag, copy=copy)



def test_svd():
	a0 = Num.array([[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, -3, -2, -1, 0, 1, 2, 3, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 1, -1, 1, -1, 1, -1, 1, 0, 0, 0, 0, 0]], Num.Float)
	a1 = Num.array([[1, 1, 1],
		[-3, -2, -1],
		[1, -1, 1]], Num.Float)
	a2 = Num.array([[1, 1, 1], [-3, -2, -1], [1, -1, 1], [0, 0, 2.2], [2, 0, 0], [0, 1, 0]],
			Num.Float)
	for a in [a0, a1, a2]:
		u, s, vh = Num.LA.svd(a)
		r = min(a.shape)
		# print 'shapes for u,s, vh=', u[:,:r].shape, s.shape, vh[:r].shape, 'r=', r
		assert Num.alltrue( s >= 0.0)
		err = Num.sum(Num.ravel(Num.dot(u[:,:r]*s, vh[:r]) - a)**2)
		assert err < 1e-6


def all_between(a, vec, b):
	return Num.alltrue(
			Num.greater_equal(vec, a)
			* Num.greater_equal(b, vec)
			)

def test_vec():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], Num.Float)
	soln = linear_least_squares(basis, y, 1e-6)
	hat = soln.hat()
	assert Num.alltrue(hat > 1.0/y.shape[0])
	assert Num.alltrue(hat < 4.0/y.shape[0])
	assert soln.rank() == 2
	print 'fitshape=', soln.fit().shape, y.shape
	err = Num.sum((soln.fit()-y)**2)
	assert 0.0 <= err < 1e-6
	print 'soln.residual=', soln.residual()
	assert all_between(-1e-6, soln.residual(), 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 1e-6
	assert abs(soln.x()[1] + 1) < 1e-6
	assert Num.sum(Num.absolute(Num.dot(basis, soln.x()) - soln.fit())) < 1e-6


def test_vec2():
	basis = Num.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
				[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0], Num.Float)
	# This test is obsolete and needs to be fixed.
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.rank() == 2
	err = Num.sum((soln.fit()-y)**2)
	avg = 10.0/11.0
	epred = 6.0*avg**2 + 5.0*(2-avg)**2
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[1] - avg) < 1e-6
	assert abs(soln.x()[0]) < 1e-6
	assert abs(err - epred) < 1e-4



def test_m1():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]])
	assert y.shape[1] == 1
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.x().shape[1] == 1
	assert soln.fit().shape[1] == 1
	assert soln.rank() == 2
	err = soln.residual()**2
	assert all_between(0, err, 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert Num.sum(Num.absolute(Num.ravel(Num.dot(basis, soln.x())-y))) < 1e-6


def test_m2():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	assert soln.rank() == 2
	err = Num.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(0.0, err, 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert abs(soln.x()[0,1] + 1) < 1e-6
	assert abs(soln.x()[1,1] - 10) < 1e-6
	assert Num.sum(Num.absolute(Num.ravel(Num.dot(basis, soln.x())-y))) < 1e-6


def test_m2r():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = reg_linear_least_squares(basis, y, Num.zeros((2,2), Num.Float), [[0.0, 0.0], [0.0, 0.0]])
	hat = soln.hat()
	assert Num.alltrue(hat > 1.0/y.shape[0])
	assert Num.alltrue(hat < 4.0/y.shape[0])
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	err = Num.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(0.0, err, 1e-6)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert abs(soln.x()[0,1] + 1) < 1e-6
	assert abs(soln.x()[1,1] - 10) < 1e-6
	assert Num.sum(Num.absolute(Num.ravel(Num.dot(basis, soln.x())-y))) < 1e-6


def test_m2rR():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = reg_linear_least_squares(basis, y, 1e6*Num.identity(2), [[0.5, 0.5],[0.5,0.5]])
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	err = Num.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(1.0, err, 500.0)
	assert abs(soln.x()[0,0] - 0.5) < 1e-3
	assert abs(soln.x()[1,0] - 0.5) < 1e-3
	assert abs(soln.x()[0,1] - 0.5) < 1e-3
	assert abs(soln.x()[1,1] - 0.5) < 1e-3
	soln = reg_linear_least_squares(basis, y, 1e6*Num.identity(2), [[0.5, 0.5],[0.5,0.5]], rscale=1.0)
	print 's', soln.x()
	print 'f', soln.fit()
	print 'r', soln.eff_rank()


def test_hat():
	"""Make sure that the hat function meets its definition."""
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y0 = Num.transpose([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	s0 = linear_least_squares(basis, y0)
	assert y0.shape[0] > 1
	for i in range(y0.shape[0]):
		y = Num.array(y0)
		y[i] += 1
		s = linear_least_squares(basis, y)
		ishift = s.fit()[i] - s0.fit()[i]
		assert -0.001 <= ishift <= 1.001
		assert abs(ishift - s0.hat()[i]) < 0.001


if __name__ == '__main__':
	test_svd()
	test_vec()
	test_m1()
	test_m2()
	test_vec2()
	test_m2r()
	test_m2rR()
	test_hat()
