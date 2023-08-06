#!/usr/bin/env python

"""A classifier that assumes that log(P) is a quadratic form.
"""


import Num
import die
import fiatio
import q_classifier_r as Q
import g_closure
import gpkmisc


COVERAGE = 3
FTEST = 0.25
N_PER_DIM = 10


class qd_classifier_desc(Q.classifier_desc):
	def __init__(self, data=None, evaluator=None, models=None, ftrim=None):
		if data is not None:
			classes = Q.list_classes(data)
			fvdim = Q.get_dim(data)	# length of the feature vector
			# print 'LIST_CLASSES'
		elif models is not None:
			classes = models.keys()
			fvdim = models.values()[0].dir.shape[0]
			# print 'MODELS.KEYS'
		Q.classifier_desc.__init__(self, classes, fvdim, models, ftrim=ftrim)

	def np(self):
		return self.ndim + 1 + (self.ndim*(self.ndim+1))/2

	def npt(self):
		return (self.nc-1) * self.np()

	def _unpm(self, prmvec):
		"""Unpack a square, symmetric matrix."""
		nd = self.ndim
		assert len(prmvec) >= (nd*(nd+1))/2
		invsigma = Num.zeros((self.ndim, self.ndim), Num.Float)
		for k in range(nd):
			tmp = prmvec[:nd-k]
			prmvec = prmvec[nd-k:]
			invsigma[k, k:] = tmp
			invsigma[k:, k] = tmp
		return (prmvec, invsigma)


	def unpack(self, prmvec, trainingset_name=None, uid=None):
		"""Produce a classifier from a parameter vector."""
		m = self.np()
		nd = self.ndim
		assert len(prmvec) == self.npt()

		# print 'UNPACK'
		o = qd_classifier(self, trainingset_name=trainingset_name, uid=uid)
		for (i, c) in enumerate(self.c):
			# print "im", i, m
			if i >= self.nc-1:
				break	# Last one is the zero model.
			pc = prmvec[i*m: (i+1)*m]
			offset = pc[0]
			pc = pc[1:]
			mu = pc[:nd]
			npc, invsigma = self._unpm(pc[nd:])
			assert len(npc) == 0
			o.add_model( c, Q.qmodel( mu, invsigma, offset))
		o.add_model( c, Q.qzmodel(self.ndim))
		# print '#UP:', o
		return o


	def start(self, data):
		"""Starting position for Markov Chain Monte Carlo."""
		m = self.np()
		data_in_class = {}
		all_data_vecs = []
		for c in self.c:
			data_in_class[c] = []
		for datum in data:
			data_in_class[datum.classid].append( datum.value )
			all_data_vecs.append( datum.value )
		amu = gpkmisc.median_across( all_data_vecs )
		mu = {}
		for c in self.c:
			assert len(data_in_class[c]) > 0
			mu[c] = gpkmisc.median_across(data_in_class[c])
			# print '#Mu[', c, ']=', mu[c]

		if len(data) < 2:
			cov = Num.identity(amu.shape[0], Num.Float)
		else:
			cov = Num.zeros((amu.shape[0], amu.shape[0]), Num.Float)
			for datum in data:
				# print '#dval', datum.value
				tmp = datum.value - amu
				# print '#tmp', c, tmp
				cov += Num.outerproduct(tmp, tmp)
			cov /= len(data)
		# print '#cov=', cov
		tr = Num.sum(Num.diagonal(cov))
		trf = 0.01*tr/cov.shape[0]
		# print '# tr=', tr, trf
		for i in range(cov.shape[0]):
			cov[i,i] += trf

		invsigma = Num.LA.inv(cov)
		# Use Mu!
		# print '#cov+ =', cov
		npt = self.npt()
		prmvec = Num.zeros((npt,), Num.Float)
		V = Num.zeros((npt, npt), Num.Float)
		j = 0
		assert len(self.c) == self.nc
		for (i, c) in enumerate(self.c):
			if i >= self.nc-1:
				break	# Last one is the zero classifier
			pc = prmvec[i*m: (i+1)*m]
			Vc = V[i*m:(i+1)*m, i*m:(i+1)*m]
			pc[0] = 0.0	# offset
			Vc[0,0] = 1.0
			j = self.ndim + 1
			pc[1:j] = mu[c]
			Vc[1:j, 1:j] = cov
			for k in range(self.ndim):
				# print "pc:", pc
				# print "invsigma:", invsigma
				w = self.ndim-k
				# print "j", j, w, j+w, c, k
				pc[j:j+w] = invsigma[k, k:k+w]
				# print "pc2:", pc
				j += w
			for jj in range(self.ndim+1, j):
				Vc[jj, jj] = pc[jj]**2
			# print "pcf:", pc
			assert j == self.np()

		check = self.unpack(prmvec)
		# print '#Check=', check	# Looking at the last term in self.c:
		for (i, c) in enumerate(self.c):
			if i < self.nc-1:
				# print '# CC=', c
				# print '# \t check.cm[c]=', check.class_models[c]
				assert check.class_models[c].bias() == 0.0
				assert Num.sum(Num.absolute(check.class_models[c].mu()-mu[c])) < 0.001
				assert Num.sum(Num.ravel(Num.absolute(check.class_models[c].invsigma()-invsigma))) < 0.001
			else:
				assert check.class_models[c].bias() == 0.0
				assert Num.sum(Num.absolute(check.class_models[c].mu())) < 0.001
				assert Num.sum(Num.ravel(Num.absolute(check.class_models[c].invsigma()))) < 0.001
		# print '#prmvec=', prmvec
		# print '#V=', V
		return (prmvec, V)

	def typename(self):
		return 'quadratic_discriminant_classifier'






class qd_classifier(Q.classifier, Q.forest_mixin):
	def __init__(self, cdesc=None, models=None, trainingset_name=None, uid=None):
		if cdesc is None:
			cdesc = qd_classifier_desc(models=models)
			
		if models is None:
			models = {}
		Q.classifier.__init__(self, cdesc.typename(),
					models, trainingset_name=trainingset_name,
					uid=uid)
		Q.forest_mixin.__init__(self, cdesc)






def go_auto(fd, coverage=COVERAGE, ftest=FTEST, n_per_dim = N_PER_DIM,
			ftrim=None, evnm=None):
	d = Q.read_data(fd)
	modelchoice = g_closure.Closure(qd_classifier_desc, g_closure.NotYet,
					evaluator=Q.evaluator_from_name(evnm),
					ftrim=ftrim)
	classout = fiatio.writer(open('classified.fiat', 'w'))
	classout.header('evaluator', evnm)
	classout.header('ftrim', ftrim)
	summary, out, wrong = Q.compute_self_class(d, coverage=coverage, ftest=ftest,
						n_per_dim = n_per_dim,
						modelchoice = modelchoice,
						builder=Q.forest_build,
						classout=classout)
	Q.default_writer(summary, out, classout, wrong)






def test_build3(classifier_choice):
	print 'TEST_BUILD3:'
	data = [
		Q.datum_tr([1.0], 'A'), Q.datum_tr([-0.01], 'B'), Q.datum_tr([2.01], 'C'),
		Q.datum_tr([1.02], 'A'), Q.datum_tr([-0.02], 'B'), Q.datum_tr([2.02], 'C'),
		Q.datum_tr([1.01], 'A'), Q.datum_tr([0.0], 'B'), Q.datum_tr([2.0], 'C'),
		Q.datum_tr([0.98], 'A'), Q.datum_tr([0.02], 'B'), Q.datum_tr([1.99], 'C'),
		Q.datum_tr([0.99], 'A'), Q.datum_tr([0.01], 'B'), Q.datum_tr([1.98], 'C'),
		]
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=None)
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = 0
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		if eval < 1:
			ok = 1
			break
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")



def test_build1q(classifier_choice):
	import random
	print 'TEST_BUILD1q:'
	data = []
	for i in range(9):
		data.append( Q.datum_tr([random.random()], 'A'))
		data.append( Q.datum_tr([random.random()+2.0], 'B'))
		data.append( Q.datum_tr([random.random()+4.0], 'A'))
	for datum in data:
		print 'd=', datum
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=None, ftrim=None)
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = 0
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		if eval < 1:
			ok = 1
			break
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")



def test_build1tq(classifier_choice):
	import random
	print 'TEST_BUILD1tq:'
	data = [ Q.datum_tr([-10.0], 'B') ]	# One spurious point to be trimmed off.
	for i in range(30):
		data.append( Q.datum_tr([random.random()], 'A'))
		data.append( Q.datum_tr([random.random()+2.0], 'B'))
		data.append( Q.datum_tr([random.random()+4.0], 'A'))
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=None, ftrim=(0.1, 6))
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = 0
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		if eval < 2:
			ok = 1
			break
		else:
			print 'eval=', eval
			print 'cdef=', cdef
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")




def test():
	from l_classifier import test_build1, test_build32, test_build2
	from l_classifier import test_2_bias, test_4_2, test_build1t
	from l_classifier import test_2_scale
	cc = qd_classifier_desc
	test_build1(cc)
	test_build1q(cc)
	# test_build1t(cc)
	test_build1tq(cc)
	test_build32(cc)
	test_build2(cc)
	test_2_scale(cc)
	test_build3(cc)
	# test_var()
	test_2_bias(cc)
	test_4_2(cc)


PSYCO = 1

if __name__ == '__main__':
	import sys

	if PSYCO:
		try:
			import psyco
			psyco.full(memory=10000)
		except ImportError:
			pass

	ftrim = None
	arglist = sys.argv[1:]
	evnm = None
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-coverage':
			COVERAGE = float(arglist.pop(0))
		elif arg == '-nperdim':
			N_PER_DIM = int(arglist.pop(0))
		elif arg == '-evaluator':
			evnm = arglist.pop(0)
		elif arg == '-ftest':
			FTEST = float(arglist.pop(0))
			assert 0.0 < FTEST < 1.0
		elif arg == '-c':
			ftrim = float(arglist.pop(0))
			assert 0.0 <= ftrim < 0.5
		elif arg == '-D':
			Q.D = 1
		elif arg == '-test':
			test()
			break
		else:
			die.die('Unrecognized argument: %s' % arg)
	go_auto(sys.stdin, coverage=COVERAGE, n_per_dim = N_PER_DIM,
		ftrim=ftrim, evnm=evnm)
