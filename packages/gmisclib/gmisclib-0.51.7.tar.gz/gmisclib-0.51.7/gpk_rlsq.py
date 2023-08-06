import Num
import gpk_lsq
import gpkavg


class NotEnoughData(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


class w_linear_least_squares(gpk_lsq.linear_least_squares):
	def __init__(self, a, y, w, minsv=None, minsvr=None, copy=True):
		a = Num.asarray(a, Num.Float)
		if len(a.shape) != 2:
			raise ValueError, "a needs to be 2-dimensional: shape=%s" % str(a.shape)

		self.w = Num.array(w, Num.Float, copy=copy)
		if len(self.w.shape) != 1 and self.w.shape[0] != a.shape[0]:
			raise ValueError, "w needs to be 1-dimensional and match a: shape=%s vs %s" % (str(self.w.shape), str(a.shape))

		aw = self.w[:,Num.NewAxis] * a
		gpk_lsq.linear_least_squares.__init__(self, aw, y, minsv=minsv,
								minsvr=minsvr, copy=copy)

	def fit(self, copy=False):
		return gpk_lsq.linear_least_squares.fit(self, copy=False)/self.w

	def y(self, copy=True):
		return gpk_lsq.linear_least_squares.y(self, copy=False)/self.w

	def set_y(self, y, copy=True):
		if y is not None:
			y = self.w * y
		gpk_lsq.linear_least_squares.set_y(self, y, copy=False)
		




class robust_linear_fit(w_linear_least_squares):
	HTMIN = 3.0
	STMIN = 1.5

	def __init__(self, a, y, sigma_y=None, minsv=None, minsvr=None):
		"""This does bounded influence regression, with
		a robust M-estimator in the y-direction.
		"""

		y = Num.asarray(y, Num.Float)
		assert len(y.shape) == 1
		ndat = y.shape[0]
		if sigma_y is None:
			sigma_y = 1.0
		if isinstance(sigma_y, (float, int)):
			self.sigma_y = sigma_y * Num.ones(y.shape, Num.Float)
		else:
			self.sigma_y = Num.asarray(sigma_y, Num.Float)
			assert len(self.sigma_y.shape) == 1
			assert self.sigma_y.shape[0] == ndat

		a = Num.asarray(a, Num.Float)
		assert len(a.shape) == 2
		assert a.shape[0] == ndat
		
		if a.shape[1] >= ndat:
			raise NotEnoughData, "Not enough data to bound influence function"

		w = 0
		w_hat = Num.ones(y.shape, Num.Float)
		w_resid = Num.ones(y.shape, Num.Float)
		hthresh = 6*self.HTMIN
		sthresh = 6*self.STMIN
		endgame = False
		while 1:
			last_w = w
			w = w_hat * w_resid
			if Num.alltrue( Num.absolute(w-last_w) < 0.01 ):
				if endgame:
					break
				else:
					hthresh = self.HTMIN
					sthresh = self.STMIN
					endgame = True
					# print 'ENDGAME'

			# print 'w=', w
			# print 'y=', y

			self.w = w
			wsig = w/self.sigma_y

			w_linear_least_squares.__init__(self, a, y, wsig, minsv=minsv, minsvr=minsvr)

			ht = (1 - 2.0/y.shape[0])/hthresh
			# print 'hat=', self.hat()
			if Num.sometrue(self.hat() >= 1.0):
				raise NotEnoughData, "Cannot bound influence of point(s)."
			hatfac = (1-self.hat())/ht
			# print 'hatfac=', hatfac
			w_hat = Num.minimum(1.0, w_hat*hatfac**0.5)
			# Keep largest weight at unity:
			w_hat = w_hat/w_hat[Num.argmax(w_hat)]
			# print 'w_hat=', w_hat

			normerr = (y - self.fit())/self.sigma_y
			# print 'normerr=', normerr
			self.typdev = gpkavg.avg(Num.absolute(normerr), None, 0.25)[0]
			r_bar = self.typdev * sthresh
			# print 'rbar=', r_bar
			w_resid = 0.5*(w_resid + Num.hypot(1, normerr/r_bar)**(-1.0) )
			wrs = Num.sqrt( Num.sum(w_resid**2, axis=0)/ndat )
			Num.divide(w_resid, wrs, w_resid)
			# print 'w_resid=', w_resid

			hthresh = self.HTMIN + 0.5*(hthresh-self.HTMIN)
			sthresh = self.STMIN + 0.5*(sthresh-self.STMIN)
			# print 'ht, st=', hthresh, sthresh
		# print "END"



def test_w1():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0.0, 1, 2, 3, 4, 5, 6, 7, 18.01, 99])
	w = Num.array([1, 3.2, 1, 1, 5, 1, 1, 1, .0001, 1])
	soln = w_linear_least_squares(basis, y, w)
	print 'soln.x', soln.x()
	print 'soln.fit', soln.fit()
	assert len(soln.x().shape) == 1
	assert len(soln.fit().shape) == 1
	assert soln.rank() == 2
	print 'residual=', soln.residual()
	assert Num.sum(Num.absolute(soln.residual()) > 0.2) == 1
	assert Num.sum(Num.absolute(soln.residual()) > 10.2) == 0
	err = Num.sum((soln.fit()-y)**2)
	assert err>=0
	assert Num.sum(err > 0.02) == 1
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 0.01
	assert abs(soln.x()[1] + 1) < 0.01
	assert Num.sum(Num.absolute(w-soln.w)) < 1e-6
	assert Num.sum(Num.absolute(Num.dot(basis, soln.x())-soln.fit())) < 1e-6



def test_w1b():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0.01, 1, 2.01, 3, 3.99, 5, 6.01, 7, 88.01, 99])
	w = Num.array([0.2, 1, 0.2, 5, 1, 0.2, 1, 2, .001, 0.01])
	soln = w_linear_least_squares(basis, y, w)
	print 'soln.x', soln.x()
	print 'soln.resid', soln.residual()
	assert Num.sum(Num.absolute(soln.residual()) > 0.05) == 1
	assert abs(soln.x()[0] - 1) < 0.01
	assert abs(soln.x()[1] + 1) < 0.01
	print 'sf', soln.fit()
	print 'mm', Num.matrixmultiply(basis, soln.x())
	assert Num.sum(Num.absolute(Num.matrixmultiply(basis, soln.x())
							-soln.fit())
				) < 1e-6

def test_r1():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0.01, 1, 1.99, 3, 4.01, 5, 5.99, 7, 88.01, 99])
	soln = robust_linear_fit(basis, y, 1)
	print 'soln.x', soln.x
	assert len(soln.x().shape) == 1
	assert len(soln.fit().shape) == 1
	assert soln.rank() == 2
	err = Num.sum((soln.fit()-y)**2)
	assert err>=0
	assert Num.sum(err > 0.02) == 1
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 0.02
	assert abs(soln.x()[1] + 1) < 0.02
	assert Num.sum(Num.absolute(Num.matrixmultiply(basis, soln.x())
						-soln.fit())
				) < 1e-5

def test_r1hat():
	basis = Num.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100],
				[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = Num.array([0.01, 1, 1.99, 3, 4.01, 5, 5.99, 7, 8, 90])
	soln = robust_linear_fit(basis, y, 1)
	print 'soln.x', soln.x
	assert soln.rank() == 2
	print 'resid=', soln.residual()
	assert Num.sum(Num.absolute(soln.residual()) > 0.04) == 1
	assert abs(soln.x()[0] - 1) < 0.05
	assert abs(soln.x()[1] + 1) < 0.05
	assert Num.sum(Num.absolute(Num.matrixmultiply(basis, soln.x())
						- soln.fit())
			) < 1e-5


if __name__ == '__main__':
	test_w1()
	test_w1b()
	test_r1()
	test_r1hat()
