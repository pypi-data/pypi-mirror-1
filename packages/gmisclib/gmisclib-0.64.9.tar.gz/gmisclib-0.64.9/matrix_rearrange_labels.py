#!/usr/bin/env python

from gmisclib import Num
from gmisclib import blue_data_selector
from gmisclib import die



def _mswap(sw1, sw2, m):
	"""Swap rows and columns in matrix m.
	Produces a copy of the matrix.
	@param m: matrix
	@param sw1: how to re-arrange rows(columns?)
	@param sw2: how to re-arrange columns(rows?)
	"""
	assert sw1.shape == (m.shape[0],)
	assert sw2.shape == (m.shape[1],)
	m1 = Num.take(m, sw1, axis=0)
	return Num.take(m1, sw2, axis=1)


def _lswap(swv, m):
	"""Swap labels in list m, according to mapping swv.
	Produces a new list.
	"""
	assert swv.shape == (len(m),)
	return [ m[swv[i]] for i in range(len(m)) ]



class diagfom(object):
	"""A class that defines a figure-of-merit for a matrix.
	"""
	def __init__(self, n, sign=1):
		"""@param sign: if sign=1, the f-o-m returned by L{eval}
			will be minimal when
			the most positive matrix elements are on the diagonal.
			If sign=-1, you'll get minimal fom with the
			the most positive elements off diagonal.
		@type sign: int
		@param n: dimension of matrix.
		@type n: int
		"""
		ar = Num.arrayrange(n)
		self.weight = sign*Num.absolute(ar[:,Num.NewAxis] - ar[Num.NewAxis,:])

	def eval(self, swv, m):
		"""Evaluate the figure of merit for a matrix m with the
		specified swap vector.
		@param m: matrix
		@param swv: swap vector
		@return: figure of merit
		@rtype: int or float (according to the type of m).
		"""
		m2 = _mswap(swv, swv, m)
		# return Num.sum(Num.ravel(m2*self.weight))
		return Num.sum(m2*self.weight)


class diagfom2(object):
	def __init__(self, n1, n2):
		a1 = Num.arrayrange(n1)
		a2 = Num.arrayrange(n2)
		self.weight = Num.absolute(a1[:,Num.NewAxis]/float(n1-1) - a2[Num.NewAxis,:]/float(n2-1))

	def eval(self, sw1, sw2, m):
		m2 = _mswap(sw1, sw2, m)
		# return Num.sum(Num.ravel(m2*self.weight))
		return Num.sum(m2*self.weight)


class blockfom(object):
	def __init__(self, n1, n2):
		pass

	def eval(self, sw1, sw2, m):
		m2 = _mswap(sw1, sw2, m)
		o = 0.0
		# o += Num.sum(Num.ravel(Num.absolute(m2[1:,:] - m2[:-1,:])))
		# o += Num.sum(Num.ravel(Num.absolute(m2[:,1:] - m2[:,:-1])))
		o += Num.sum(Num.absolute(m2[1:,:] - m2[:-1,:]))
		o += Num.sum(Num.absolute(m2[:,1:] - m2[:,:-1]))
		return o


def symm_swap_toward_minimal_fom(m, fom, maxtries):
	n = m.shape[0]
	assert m.shape == (n, n)
	swv = Num.arrayrange(n)
	of = fom.eval(swv, m)
	sincelast = 0
	bds = blue_data_selector.bluedata( [ (i,j) for i in range(n) for j in range(n) if i!=j ] )
	if maxtries is None:
		maxtries = 2*n*n
	for (i,j) in bds:
		oswv = Num.array(swv, Num.Int, copy=True)
		swv[i], swv[j] = (swv[j], swv[i])
		nf = fom.eval(swv, m)
		if nf < of:
			of = nf
			sincelast = 0
		else:
			swv = oswv
			sincelast += 1
		if sincelast > maxtries:
			break
	return swv


def swap_toward_minimal_fom(m, fom, maxtries):
	n1, n2 = m.shape
	assert m.shape == (n1, n2)
	sw1 = Num.arrayrange(n1)
	sw2 = Num.arrayrange(n2)
	of = fom.eval(sw1, sw2, m)
	sincelast = 0
	bd1 = blue_data_selector.bluedata( [ (i,j) for i in range(n1) for j in range(n1) if i!=j ] )
	bd2 = blue_data_selector.bluedata( [ (i,j) for i in range(n2) for j in range(n2) if i!=j ] )
	if maxtries is None:
		maxtries = 2*(n1*n1 + n2*n2)
	else:
		maxtries = 2*maxtries
	while True:
		i, j = bd1.pick(1)[0]
		osw1 = Num.array(sw1, Num.Int, copy=True)
		sw1[i], sw1[j] = (sw1[j], sw1[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			of = nf
			sincelast = 0
		else:
			sw1 = osw1
			sincelast += 1

		i, j = bd2.pick(1)[0]
		osw2 = Num.array(sw2, Num.Int, copy=True)
		sw2[i], sw2[j] = (sw2[j], sw2[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			of = nf
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			sincelast = 0
		else:
			sw2 = osw2
			sincelast += 1

		i, j = bd1.pick(1)[0]
		osw1 = Num.array(sw1, Num.Int, copy=True)
		sw1[i], sw1[j] = (sw1[j], sw1[i])
		i, j = bd2.pick(1)[0]
		osw2 = Num.array(sw2, Num.Int, copy=True)
		sw2[i], sw2[j] = (sw2[j], sw2[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			of = nf
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			sincelast = 0
		else:
			sw1 = osw1
			sw2 = osw2
			sincelast += 1

		if sincelast > maxtries:
			break
	return (sw1, sw2)



def swap_toward_diag(m, lbls, maxtries=None):
	"""Swap the rows and columns of a matrix to bring it closer to a diagonal
	matrix: i.e. large entries on the main diagonal and small entries
	away from the main diagonal.    Rows and columns are swapped together,
	so that the ordering or rows will match the ordering of columns.
	"""
	
	fom = diagfom(len(lbls))
	swv = symm_swap_toward_minimal_fom(Num.absolute(m), fom, maxtries)
	return ( _mswap(swv, swv, m), _lswap(swv, lbls) )


def swap_toward_diag2(m, lbl1, lbl2, maxtries=None):
	"""Swap the rows and columns of a matrix to make it roughly
	diagonal:
	i.e. large entries on the main diagonal and small entries
	away from the main diagonal.   Note that this will work
	even if the matrix is not square.
	"""
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(Num.absolute(m), fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def pos_near_diag2(m, lbl1, lbl2, maxtries=None):
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def neg_near_diag2(m, lbl1, lbl2, maxtries=None):
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(-m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def swap_toward_blocks(m, lbl1, lbl2, maxtries=None):
	"""Swap rows and columns of a matrix to bring it closer to a block
	form, where similar values occur together in blocks.
	"""
	fom = blockfom(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )
