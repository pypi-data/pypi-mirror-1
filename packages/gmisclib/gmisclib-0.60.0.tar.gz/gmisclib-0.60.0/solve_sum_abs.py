"""Solves various equations involving minimizing the
sum of absolute values of things.
"""


import math
from gmisclib import Num
from gmisclib import Numeric_gpk
from gmisclib import root

def solve1(y0, y1):
	"""We minimize the equation sum_over_i(abs(y0_i*(1-x) + y1_i*x))
	to find the best x.   Returns x.
	I don't know if this is strictly correct.
	"""
	n = len(y0)
	assert len(y1)==n
	yy0 = Num.asarray(y0)
	yy1 = Num.asarray(y1)
	slp = yy1-yy0
	zro = -yy0/slp
	i = Num.argsort(zro)
	zros = Num.take(zro, i, axis=0)
	slps = Num.absolute(Num.take(slp, i, axis=0))
	islps = Num.add.accumulate(slps)
	isl_tgt = 0.5*islps[-1]
	minidx = Num.searchsorted(islps, [isl_tgt])
	return zros[minidx]


def solve_fit(x, y, eps = 1e-7):
	"""Solves for the line y_hat = m*x + b that minimizes
	sum(abs(y - y_hat)).
	Algorithm from Numerical Recipes, Volume 2.
	Returns (mhat, bhat).
	"""
	assert eps > 0.0
	x = Num.asarray(x)
	y = Num.asarray(y)

	def b(x, y, m):
		return Numeric_gpk.N_median(y-m*x)

	mp2 = math.pi / 2.0

	def to_be_zeroed(theta, xy):
		x, y = xy
		if theta == mp2:
			return Num.sum(x * Num.sign(-x))
		if theta == -mp2:
			return Num.sum(x * Num.sign(x))

		m = math.tan(theta)
		bhat = b(x, y, m)
		return Num.sum(x * Num.sign(y - m*x - bhat) )

	mhat =  math.tan( root.root(to_be_zeroed, -mp2, mp2, (x, y),
					0.0,
					eps*Num.sum(Num.absolute(y))
					)
			)
	return (mhat, b(x, y, mhat))


def test1():
	assert solve1([-1], [1]) == 0
	assert solve1([0.5, 1], [0.1, 0]) == 1
	assert solve1([1.1, 0.6], [0, 0.1]) == 1


def test2():
	print solve_fit([0,1], [0,1])
	print solve_fit([0,1], [0,0.5])
	print solve_fit([0,1], [0,2])
	print solve_fit([0,1], [1,2])
	print solve_fit([math.exp(1),math.pi], [math.sqrt(2.0),1.0/97.0])

if __name__ == '__main__':
	test1()
	test2()
