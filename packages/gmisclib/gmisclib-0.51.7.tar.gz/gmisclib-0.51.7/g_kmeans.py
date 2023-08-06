#!/usr/bin/env python


import math
import random
import q_classifier_r
import g_implements
import Num
import gpkmisc
import Numeric_gpk as NG
import fiatio
import chunkio
import die

HUGE = 1e30
Clip = None

def find_which_cluster(datum, cpos, distfcn):
	bestdist = HUGE
	best = -1
	for (i, cp) in enumerate(cpos):
		tmp = distfcn(datum.value, cp)
		if tmp < bestdist:
			bestdist = tmp
			best = i
	return (best, bestdist)


def find_center(i, membership, data, clip):
	tmp = []
	for (mem, datum) in enumerate(membership, data):
		if mem == i:
			tmp.append( datum.value )
	ctr = NG.trimmed_mean_across(tmp, None, clip)
	return ctr


class cluster_descriptor:
	def __init__(self, center, membership, size):
		self.center = center
		self.membership = membership
		self.size = size



def kmeans(data, Ncl, distfcn=None, Nit=None, clip=None):
	for datum in data:
		g_implements.check(datum, q_classifier_r.datum_c)
	
	if Nit is None:
		Nit = 10 + int(round(math.sqrt(len(data)*Ncl)))
	if clip is None:
		clip = 0.10
	assert len(data) >= Ncl
	bestcp = None
	bestm = None
	besterr = HUGE
	starts = 0
	while starts < Nit:
		cpos = [data[c].value for c in random.sample(range(len(data)), Ncl) ]
		membership = Num.zeros((len(data),), Num.Int)
		assert len(cpos) == Ncl
		passes = 0
		while passes < Nit:
			cldtmp = [ [] for x in range(Ncl) ]
			scatter = 0.0
			omem = Num.array(membership, copy=True)
			for (i, datum) in enumerate(data):
				membership[i], dist = find_which_cluster(datum, cpos, distfcn)
				if membership[i] >= 0:
					cldtmp[membership[i]].append(dist)
				scatter += dist
			cldist = [ gpkmisc.median(cldtmp[i]) for i in range(Ncl) ]

			for i in range(Ncl):
				cpos[i] = find_center(i, membership, data, clip)
			if omem == membership:
				break
			passes += 1

		if scatter < besterr:
			besterr = scatter
			bestcp = cpos
			bestm = membership

		starts += 1

	o = []
	for i in range(Ncl):
		m = [ d.uid for (mem, d) in zip(bestm, data) if mem == i ]
		o.append( cluster_descriptor(bestcp[i], m, cldist[i]) )
	map_to_cluster = {}
	for (datum, mem) in zip(data, bestm):
		map_to_cluster[datum] = mem
	return (o, map_to_cluster, besterr)




def read_data(fd):
	"""Reads in feature vectors, each with a uid as a comment."""
	d = []
	dim = None
	# die.info('Reading')
	ln = 0
	# for l in fd.readlines():
	for l in fd:
		ln += 1
		if l.startswith('#'):
			continue
		aa = l.split('#', 1)
		if len(aa) > 1:
			uid = aa[1].strip()
		else:
			uid = 'Line:%d' % ln
		a = aa[0].split()
		if dim is None:
			dim = len(a)
		elif len(a) != dim:
			die.die('Not all vectors have length=%d.  Problem on line %d'
					% (dim, ln)
				)
		d.append( q_classifier_r.datum_c(Num.array([float(x) for x in a]),
				uid)
				)
	return d


def euclid(a, b):
	return math.sqrt(Num.sum(Num.ravel(a-b)**2))


if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	hdrs = {}
	uidname = 'uid'
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-header':
			k = arglist.pop(0)
			v = arglist.pop(0)
			hdrs[k] = v
		elif arg == '-uidname':
			uidname = arglist.pop(0)
		elif arg == '-clip':
			Clip = float(arglist.pop(0))
		else:
			die.die('Unrecognized flag: %s' % arg)
	ncl = int(arglist[0])
	d = read_data(sys.stdin)
	o, map_to_cluster, err = kmeans(d, ncl, distfcn=euclid, clip=Clip)
	w = fiatio.writer(sys.stdout)
	w.headers(hdrs)
	w.header('Ncl', ncl)
	if Clip is not None:
		w.header('Clip', Clip)
	w.header('Error', err)
	for (clnum, descr) in enumerate(o):
		w.header('cluster%d' % clnum,
			chunkio.chunkstring_w().write_NumArray(descr.center, str).close()
			)
		w.header('size%d' % clnum, descr.size)
	for (clnum, descr) in enumerate(o):
		for datum_uid in descr.membership:
			tmp = {'clnum': clnum, uidname: datum_uid}
			w.datum(tmp)
	w.close()
