#!/usr/bin/env python

import Num
import blue_data_selector
import die



def _mswap(sw1, sw2, m):
	"""Swap rows and columns in matrix m, according to mapping swv.
	Produces a copy of the matrix."""
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
	def __init__(self, n):
		ar = Num.arrayrange(n)
		self.weight = Num.absolute(ar[:,Num.NewAxis] - ar[Num.NewAxis,:])

	def eval(self, swv, m):
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


def diag_swap_toward_minimal_fom(m, lbls, fom, maxtries):
	n = len(lbls)
	assert m.shape == (n, n)
	swv = Num.arrayrange(n)
	of = fom.eval(swv, m)
	sincelast = 0
	bds = blue_data_selector.bluedata( [ (i,j) for i in range(n) for j in range(n)] )
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
	return ( _mswap(swv, swv, m), _lswap(swv, swv, lbls) )


def swap_toward_minimal_fom(m, lbl1, lbl2, fom, maxtries):
	n1 = len(lbl1)
	n2 = len(lbl2)
	assert m.shape == (n1, n2)
	sw1 = Num.arrayrange(n1)
	sw2 = Num.arrayrange(n2)
	of = fom.eval(sw1, sw2, m)
	sincelast = 0
	bd1 = blue_data_selector.bluedata( [ (i,j) for i in range(n1) for j in range(n1)] )
	bd2 = blue_data_selector.bluedata( [ (i,j) for i in range(n2) for j in range(n2)] )
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
		if sincelast > maxtries:
			break
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )



def swap_toward_diag(m, lbls, maxtries=None):
	fom = diagfom(len(lbls))
	return diag_swap_toward_minimal_fom(m, lbls, fom, maxtries)


def swap_toward_diag2(m, lbl1, lbl2, maxtries=None):
	fom = diagfom2(len(lbl1), len(lbl2))
	return swap_toward_minimal_fom(m, lbl1, lbl2, fom, maxtries)


def swap_toward_blocks(m, lbl1, lbl2, maxtries=None):
	fom = blockfom(len(lbl1), len(lbl2))
	return swap_toward_minimal_fom(m, lbl1, lbl2, fom, maxtries)
