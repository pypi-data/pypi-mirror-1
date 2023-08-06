#!/usr/bin/env python

"""A classifier that assumes that P is linear in position.
This is known as a (linear) logistic discriminant analysis::

@inbook{webb:spr:logistic,
   author    = {Andrew Webb},
   title     = {Statistical Pattern Recognition},
   pages     = {124--132},
   year      = {1999},
   publisher = {Arnold},
   address   = {London, New York},
   note = {ISBN 0 340 74164  3}
}
"""


import Num
import chunkio
import die
import fiatio
import q_classifier_r as Q
import g_closure
import gpkmisc
import Numeric_gpk
import math
import random
import sys

COVERAGE = 3
FTEST = 0.25
N_PER_DIM = 10


def ref_from_data(data):
	tmp = [ datum.value for datum in data ]
	return gpkmisc.median_across(tmp)


def ref_from_models(models):
	tmp = [m.reference for m in models.values()]
	return gpkmisc.median_across(tmp)


class l_classifier_desc(Q.classifier_desc):
	def __init__(self, data=None, evaluator=None, models=None, ftrim=None):
		if data is not None:
			classes = Q.list_classes(data)
			fvdim = Q.get_dim(data)	# length of the feature vector
			reference_pt = ref_from_data(data)
			# print 'LIST_CLASSES'
		elif models is not None:
			classes = models.keys()
			fvdim = models.values()[0].direction.shape[0]
			reference_pt = ref_from_models(models)
			# print 'MODELS.KEYS'
		Q.classifier_desc.__init__(self, classes, fvdim, models, ftrim=ftrim)
		self.reference = reference_pt
		self.evaluator = evaluator


	def np(self):
		"""The number of parameters required to define each class."""
		assert self.ndim > 0
		return self.ndim + 1

	def npt(self):
		"""The total number of parameters required to define all classes."""
		assert self.nc > 1
		assert self.np() > 0
		return (self.nc-1) * self.np()

	def unpack(self, prmvec, trainingset_name=None, uid=None):
		"""Produce a classifier from a parameter vector."""
		m = self.np()
		assert len(prmvec) == self.npt()
		assert self.c	# Can't do much with zero classes.

		o = l_classifier(self, trainingset_name=trainingset_name, uid=uid)
		for (i, c) in enumerate(self.c):
			if i >= self.nc-1:
				break	# Last one is the zero model.
			# print 'ic', i, c, i*m, (i+1)*m, prmvec.shape
			pc = prmvec[i*m : (i+1)*m]
			bias = pc[0]
			prms = pc[1:]
			o.add_model( c, Q.lmodel( prms, bias, self.reference ) )
		o.add_model(c, Q.lzmodel( self.ndim ) )
		return o


	def start(self, data):
		"""Starting position for Markov Chain Monte Carlo."""
		assert self.npt() > 0
		p = Num.zeros((self.npt(),), Num.Float)
		v = Num.identity(self.npt(), Num.Float)
		var = Numeric_gpk.vec_variance( [datum.value for datum in data] )
		print 'data[0].value=', data[0].value
		print 'START: var=', var
		assert var.shape == (self.ndim,)
		assert self.npt() % self.np() == 0
		for i in range(self.npt()):
			snp = self.np()
			isnp = i % snp
			if isnp == 0:
				sig = 1.0
			else:
				sig = math.sqrt(var[isnp-1])
			p[i] = random.normalvariate(0.0, 1.0/sig)
			v[i,i] = sig**-2
		print 'p=', p
		print 'v=', v
		return (p, v)

	def typename(self):
		return 'linear_discriminant_classifier'






class l_classifier(Q.classifier, Q.forest_mixin):
	def __init__(self, cdesc=None, models=None, trainingset_name=None, uid=None):
		if cdesc is None:
			cdesc = l_classifier_desc(models=models)
		if models is None:
			models = {}
		Q.classifier.__init__(self, cdesc.typename(), models,
					trainingset_name=trainingset_name, uid=uid)
		Q.forest_mixin.__init__(self, cdesc)
	





def go_auto(fd, coverage=COVERAGE, ftest=FTEST, n_per_dim = N_PER_DIM,
			ftrim=None, evnm=None, verbose=True):
	data = Q.read_data(fd)
	modelchoice = g_closure.Closure(l_classifier_desc, g_closure.NotYet,
					evaluator=Q.evaluator_from_name(evnm),
					ftrim=ftrim)
	classout = fiatio.writer(open('classified.fiat', 'w'))
	classout.header('evaluator', evnm)
	classout.header('ftrim', ftrim)
	summary, out, wrong = Q.compute_self_class(data, coverage=coverage, ftest=ftest,
						n_per_dim = n_per_dim,
						modelchoice = modelchoice,
						builder=Q.forest_build,
						classout=classout,
						verbose=verbose)
	Q.default_writer(summary, out, classout, wrong)




def classifier_reader(dc):
	"""Read the classifier definitions produced by classifier_writer()."""
	def model_reader(dc):
		if dc.groupstart() != 'linear_class_description':
			raise chunkio.BadFileFormat, "Wrong type of class description"
		bias = dc.read_float()
		direction = dc.read_NumArray()
		if len(direction.shape) != 1:
			raise chunkio.BadFileFormat, "Bad shape direction"
		reference_pt = dc.read_NumArray()
		dc.groupend()
		q = Q.model(direction, bias, reference_pt)
		return q

	if dc.groupstart() != 'linear_discriminant_classifier':
		raise chunkio.BadFileFormat, "Missing outer group"

	models = dc.read_dict_of(model_reader)
	info = dc.read_dict(lambda x:x)
	dc.groupend()
	return l_classifier( cdesc=None, models=models, trainingset_name=info['trainingset_name'], uid=info['uid'])


def read_classes(fd):
	dc = chunkio.datachunk(fd)
	hdr = dc.read_dict(float)
	classes = dc.read_array_of(classifier_reader)
	return (hdr, classes)




def test_build1(classifier_choice):
	print 'TEST_BUILD1:'
	data = [ Q.datum_tr([1.0], 'A'), Q.datum_tr([0.0], 'B') ]
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=Q.evaluate_match)
	assert isinstance(modelchoice, Q.classifier_desc)
	print 'modelchoice=', modelchoice
	print 'data=', data
	ok = 0
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		print 'cdef=', cdef
		eigenvalue = Q.evaluate_match(cdef, data)
		print 'eval=', eigenvalue
		if eigenvalue < 1:
			ok = 1
			break
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")



def test_build1t(classifier_choice):
	print 'TEST_BUILD1t:'
	# Two bad points to be trimmed off:
	data = [ Q.datum_tr([100.0], 'A'), Q.datum_tr([-101.0], 'B') ]
	# Lots of good points:
	for i in range(30):
		data.append( Q.datum_tr([random.random()], 'A'))
		data.append( Q.datum_tr([random.random()+2.0], 'B'))
	print 'data=', data
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=Q.evaluate_match, ftrim=(0.1,6))
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = 0
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		if eval < 3:
			ok = 1
			break
		else:
			print 'eval=', eval
			print 'cdef=', cdef
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")



def test_build32(classifier_choice):
	print 'TEST_BUILD32:'
	data = [
		Q.datum_tr([1.0, 0.0], 'A'),
		Q.datum_tr([-0.01, 0.0], 'B'),
		Q.datum_tr([-.01, 1.0], 'C'),
		Q.datum_tr([1.02, 0.01], 'A'),
		Q.datum_tr([-0.02, 0.01], 'B'),
		Q.datum_tr([-.02, 1.01], 'C'),
		Q.datum_tr([1.01, -0.01], 'A'),
		Q.datum_tr([0.0, -0.01], 'B'),
		Q.datum_tr([0, 0.99], 'C'),
		Q.datum_tr([0.98, 0.02], 'A'),
		Q.datum_tr([0.02, 0.0], 'B'),
		Q.datum_tr([-0.01, 0.98], 'C'),
		Q.datum_tr([0.99, 0.01], 'A'),
		Q.datum_tr([0.01, 0.03], 'B'),
		Q.datum_tr([-.02, 0.97], 'C'),
		]
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=Q.evaluate_match)
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = False
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		print cdef
		if eval < 1:
			ok = True
			break
	if not ok:
		die.die( "can't find a perfect classifier in this trivial situation!")


def test_build2(classifier_choice):
	print 'TEST_BUILD2:'
	data = [
		Q.datum_tr([1.0, 2.0, 0.0], 'A'),
		Q.datum_tr([0.0, 1.0, 0.0], 'A'),
		Q.datum_tr([1.0, 1.0, 1.0], 'A'),
		Q.datum_tr([2.0, 0.0, 0.0], 'A'),
		Q.datum_tr([2.0, 2.0, 2.0], 'A'),
		Q.datum_tr([1.0, 0.0, 1.0], 'A'),
		Q.datum_tr([0.0, -1.0, -2.0], 'B'),
		Q.datum_tr([-1.0, -1.0, -2.0], 'B'),
		Q.datum_tr([0.0, -1.0, -1.0], 'B'),
		Q.datum_tr([-2.0, -1.0, -2.0], 'B'),
		Q.datum_tr([0.0, -1.0, 0.0], 'B'),
		Q.datum_tr([0.0, 0.0, -2.0], 'B'),
		Q.datum_tr([-2.0, -2.0, -2.0], 'B'),
		Q.datum_tr([-1.0, -1.0, 0.0], 'B')
		]
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = classifier_choice(data, evaluator=Q.evaluate_match)
	assert isinstance(modelchoice, Q.classifier_desc)
	ok = False
	for cdef in Q.forest_build(data, 40, modelchoice=modelchoice):
		eval = Q.evaluate_match(cdef, data)
		if eval < 1:
			ok = True
			break
	if not ok:
		die.die("can't find a perfect classifier in this trivial situation!")



def test_4_2(classifier_choice):
	print 'TEST_4_2:'
	data = []
	for i in range(400):
		data.append( Q.datum_tr( [ random.random() ], 'a') )
		data.append( Q.datum_tr( [ random.random() ], 'b') )
		data.append( Q.datum_tr( [ 5+2*random.random() ], 'c') )
		data.append( Q.datum_tr( [ 5+2*random.random() ], 'd') )
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = g_closure.Closure(classifier_choice, g_closure.NotYet,
					evaluator=Q.evaluate_match)
	summary, out, wrong = Q.compute_self_class(data, ftest=FTEST, coverage=COVERAGE,
						modelchoice = modelchoice,
						n_per_dim = N_PER_DIM,
						builder=Q.forest_build)
	assert abs(summary['Chance'] - 0.25) < 0.1
	assert abs(summary['Pcorrect'] - 0.5) < 0.1
	assert summary['Pcorrect'] > summary['Chance']
	print 'summary:', summary



def test_2_bias(classifier_choice):
	print 'TEST_2_bias:'
	data = []
	for i in range(400):
		data.append( Q.datum_tr( [ random.random() ], 'a') )
	for i in range(40):
		data.append( Q.datum_tr( [ random.random() ], 'b') )
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = g_closure.Closure(classifier_choice, g_closure.NotYet,
					evaluator=Q.evaluate_match)
	classout = []
	summary, out, wrong = Q.compute_self_class(data, ftest=FTEST, coverage=COVERAGE,
						modelchoice = modelchoice,
						n_per_dim = N_PER_DIM,
						builder=Q.forest_build,
						classout=classout)
	print 'summary:', summary
	assert abs(summary['Chance'] - 0.9) < 0.05
	assert abs(summary['Pcorrect'] - 0.9) < 0.05
	nbc = 0
	nbt = 0
	ntot = 0
	for tmp in classout:
		if tmp['trueclass']=='b':
			nbt += 1
		if tmp['compclass']=='b':
			nbc += 1
		ntot += 1
	print 'true b=', nbt/float(ntot), 'computed b=', nbc/float(ntot)
	assert abs(nbt/float(ntot) - 0.1) < 0.03
	assert nbc < 1.3*nbt


def _t2sguts(off, f):
	o = []
	for i in range(1,8):
		o.append( random.gauss(off*i, f*i*i) )
	return o

def test_2_scale(classifier_choice):
	print 'TEST_2_scale:'
	data = []
	for i in range(300):
		data.append( Q.datum_tr( _t2sguts(0.0, 0.001), 'a') )
	for i in range(100):
		data.append( Q.datum_tr( _t2sguts(0.0, 0.001), 'b') )
	assert issubclass(classifier_choice, Q.classifier_desc)
	modelchoice = g_closure.Closure(classifier_choice, g_closure.NotYet,
					evaluator=Q.evaluate_match)
	classout = []
	summary, out, wrong = Q.compute_self_class(data, ftest=FTEST, coverage=COVERAGE,
						modelchoice = modelchoice,
						n_per_dim = N_PER_DIM,
						builder=Q.forest_build,
						classout=classout)
	print 'summary:', summary
	assert abs(summary['Chance'] - 0.75) < 0.05
	assert abs(summary['Pcorrect'] - 0.75) < 0.10
	nbc = 0
	nbt = 0
	ntot = 0
	for tmp in classout:
		if tmp['trueclass']=='b':
			nbt += 1
		if tmp['compclass']=='b':
			nbc += 1
		ntot += 1
	print 'true b=', nbt/float(ntot), 'computed b=', nbc/float(ntot)
	assert abs(nbt/float(ntot) - 0.25) < 0.10
	assert nbc < 1.3*nbt



def test_var():
	print 'TEST_var:'
	data = []
	for i in range(80):
		data.append( Q.datum_tr( [ random.gauss(0.0, 1.0), random.gauss(0.0, 1.0) ], 'a') )
	for i in range(160):
		data.append( Q.datum_tr( [ random.gauss(0.0, 1.0), random.gauss(0.0, 1.0)+0.01 ], 'b') )
	modelchoice = g_closure.Closure(l_classifier_desc, data,
					evaluator=Q.evaluate_match)
	summary, out, wrong = Q.compute_self_class(data,
					modelchoice = modelchoice,
					builder=Q.forest_build)
	print 'summary:', summary
	# assert abs(summary['Chance'] - 0.5) < 0.1
	# assert abs(summary['Pcorrect'] - 0.75) < 0.1


def calibrate_var():
	for i in range(15):
		test_var()
		sys.stdout.flush()

def test():
	cc = l_classifier_desc
	test_build1(cc)
	test_build1t(cc)
	test_build32(cc)
	test_build2(cc)
	# test_var()
	test_2_scale(cc)
	test_2_bias(cc)
	test_4_2(cc)


PSYCO = 1

if __name__ == '__main__':

	if PSYCO:
		try:
			import psyco
			psyco.full(memory=10000)
		except ImportError:
			pass

	evnm = None
	ftrim = None
	Verbose = True
	arglist = sys.argv[1:]
	while len(arglist)>0 and arglist[0].startswith('-'):
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
		elif arg == '-c':
			ftrim = float(arglist.pop(0))
		elif arg == '-taciturn':
			verbose = False
		elif arg == '-D':
			Q.D = 1
		elif arg == '-test':
			test()
			sys.exit(0)
		else:
			die.die('Unrecognized argument: %s' % arg)
	go_auto(sys.stdin, coverage=COVERAGE, n_per_dim = N_PER_DIM,
		ftrim=ftrim, evnm=evnm, ftest=FTEST, verbose=Verbose)
