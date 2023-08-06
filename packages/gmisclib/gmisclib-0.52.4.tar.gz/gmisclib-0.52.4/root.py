
"""Solve a 1-dimensional equation to find the roots.
This does alternating secant and bisection steps.
It will work for any function, discontinuous or not.
For a nasty function, it might be a factor of 2 slower
than bisection, but for a nearly-linear function,
it can be much faster than bisection.
"""

import die


def _root1(f, xl, xh, p, fl, fh, epsx, epsf, dbg=None):
	if dbg:
		dbg.append( ('xl:%s sh:%s fl:%s fh:%s', (xl, xh, fl, fh)) )
	# print "(%f, %f) -> (%f, %f)" % (xl, fl, xh, fh)
	assert epsx >= 0.0
	assert epsf >= 0.0
	assert xh > xl
	if fl == 0:
		if dbg:
			dbg.append( ('fl==0, return xl= %s', repr(xl)) )
		return xl
	if fh == 0:
		if dbg:
			dbg.append( ('fh==0, return xh= %s', repr(xh)) )
		return xh
	if xh-xl<=epsx or abs(fl)<epsf or abs(fh)<epsf:
		tmp = xl + (xl-xh)*fl/(fh-fl)  #  (xl*fh-xh*fl)/(fh-fl)
		assert xl <= tmp <= xh, "Not xl=%.15g <= tmp=%.15g <= xh=%.15g" % (xl, tmp, xh)
		if dbg:
			dbg.append( ('xl:%s sh:%s fl:%s fh:%s tmp:%s', (xl, xh, fl, fh, tmp)) )
		if tmp > xh:
			if dbg:
				dbg.append( ('Return xh', () ) )
			return xh
		elif tmp < xl:
			if dbg:
				dbg.append( ('Return xl', () ) )
			return xl
		else:
			if dbg:
				dbg.append( ('Return tmp', () ) )
			return tmp
		

	assert (fh>0) != (fl>0)
	q = [ (xl, fl), (xh, fh) ]

	# Do a secant step...
	xsec = (xl*fh-xh*fl)/(fh-fl)
	if dbg:
		dbg.append( ('xsec=%s', xsec) )
	if xsec>xl and xsec<xh:
		fsec = f(xsec, p)
		if fsec == 0:
			if dbg:
				dbg.append( ('Fsec==0, xsec=%s', xsec) )
			return xsec
		# print "secant: (%f, %f)" % (xsec, fsec)
		q.append( (xsec, fsec) )

		if (fsec>0) == (fl>0):
			xbi = xsec + (xh-xsec)*0.5
		else:
			xbi = xsec + (xl-xsec)*0.5
	else:
		xbi = xl + 0.5*(xh - xl)
	if dbg:
		dbg.append( ('xbi=%s', xbi) )

	# ...followed by a bisection-like step.

	assert xl <= xbi <= xh, "Not xl=%.15g <= xbi=%.15g <= xh=%.15g" % (xl, xbi, xh)
	if xbi > xl and xbi < xh and xbi!=xsec:
		fbi = f(xbi, p)
		if dbg:
			dbg.append( ('fbi=%s', fbi) )
		q.append( (xbi, fbi) )

	if len(q) == 2:	# No progress is being made, presumably
			# because xl and xh are neighbouring reals.
		# print "RETURN no progress"
		if dbg:
			dbg.append( ('len(q)=%d', len(q)) )
		return 0.5*(xl+xh)

	q.sort()

	X = 0
	F = 1
	# Then, we see which interval contains the root, and focus the search on it.
	if dbg:
		dbg.append( ('q= %s', q) )
	for i in  range(1, len(q)):
		assert q[i][X] != q[i-1][X]
		if (q[i][F]>0) != (q[i-1][F]>0):
			if dbg:
				dbg.append( ('recurse i=%d [%.15g, %.15g] -> [%.15g, %.15g]',
						(i, xl, xh, q[i-1][X], q[i][X]) )
					)
			return _root1(f, q[i-1][X], q[i][X], p, q[i-1][F], q[i][F], epsx, epsf)
	raise RuntimeError, "Lost a root!"



def root(f, xl, xh, p, epsx, epsf):
	"""Find a root of an equation.
	F is the function to solve, called as f(x, p).
	P is arbitrary data for f.
	This function assumes there is known to be a root in [xl,xh].
	It finds it within a region of width epsx, or
	at least finds an x such that -epsf < f(x, p) < epsf .
	"""
	_s = []
	if xh < xl :
		return None
	fl = f(xl, p)
	if fl == 0:
		return xl
	fh = f(xh, p)
	if fh == 0:
		return xh
	if xh == xl:
		return None

	# print fl, fh
	assert (fl>0) != (fh>0), "0 or an even number of roots in initial x-range."
	try:
		return _root1(f, xl, xh, p, fl, fh, epsx, epsf, _s)
	except RuntimeError, x:
		die.warn('Runtime Error: %s' % str(x))
		for (fmt,val) in _s:
			print fmt%val
		die.die('Failed')


def _test1f(x, p):
	return 100/int(round(x)) - 10

def test():
	q = root(_test1f, 1, 1000, None, 1e-6, 0.01)
	assert _test1f(q, None) == 0
	q = root(_test1f, 1, 16, None, 1e-6, 0.01)
	assert _test1f(q, None) == 0


def iroot(y, xl, xh, epsy=0.0):
	"""Find a zero in an array y.
	This function assumes there is known to be a root in [xl,xh].
	It returns a real-number index into the array which
	linearly interpolates to zero.
	"""
	import math
	assert 0 <= xl < y.shape[0]
	assert 0 <= xh < y.shape[0]

	def interp(x, y):
		xi = math.floor(x)
		frac = x - xi
		i = int(xi)
		if frac > 0:
			return y[i] + (y[i+1]-y[i])*frac
		return y[i]

	return root(interp, xl, xh, y, 0.001, epsy)


def testi():
	import Num
	y = 0.64234*(Num.arange(100) - 32.234)
	assert abs(iroot(y, 10, 50) - 32.234) < 0.002

if __name__ == '__main__':
	test()
	testi()
