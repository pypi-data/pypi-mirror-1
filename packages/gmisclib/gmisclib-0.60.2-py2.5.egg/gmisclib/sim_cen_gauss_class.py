#!/usr/bin/env python

"""Simple centered Gaussian Classifier.
It's designed for a case where there is a lot of data and
where the data is a multivariate Gaussian.
"""


import die
import Num
import q_classifier_r as QCR
import dictops
import fiatio
import gpk_writer

COVERAGE = 3
FTEST = 0.25
Fudge = 1e-6
PSYCO = True

def logdet(cov):
	"""Returns the log of the determinant of a matrix."""
	q = Num.LA.eigvalsh(cov)
	assert Num.alltrue(q > 0)
	return Num.sum(Num.log(q))


def typ_trace(covlist):
	"""This raises all the eigenvalues a little bit,
	so that processing can proceed, even if the covariance
	is singular.   To first order, the fudge gets subtracted
	later on in the processing.
	"""
	tr = 0.0
	dim = None
	for (k, cov) in covlist.items():
		tr += Num.trace(cov)/cov.shape[0]
		if dim is None:
			dim = cov.shape[0]
		else:
			assert cov.shape[0] == dim
	tr /= len(covlist)
	return tr


def boost_diag(covlist, diagboost):
	"""This raises all the eigenvalues a little bit,
	so that processing can proceed, even if the covariance
	is singular.   To first order, the fudge gets subtracted
	later on in the processing.
	"""
	for c in covlist.values():
		trm = Num.identity(c.shape[0])*diagboost
		Num.add(c, trm, c)




def go_auto(fd, Mu=False, coverage=COVERAGE, ftest=FTEST, cb=None, cfd_file = None):
	d = QCR.read_data(fd)
	if cfd_file == None:
		classout = gpk_writer.null_writer()
	else:
		classout = fiatio.writer(open(cfd_file, 'w'))
	summary, out, wrong = QCR.compute_self_class(d, coverage=coverage, ftest=ftest,
						n_per_dim = 0,
						modelchoice = None,
						builder=cb,
						classout=classout)
	QCR.default_writer(summary, out, classout, wrong)



def _do_test(d, coverage=COVERAGE, ftest=FTEST, cb=None):
	classout = gpk_writer.null_writer()
	summary, out, wrong = QCR.compute_self_class(d, coverage=coverage, ftest=ftest,
						n_per_dim = 0,
						modelchoice = None,
						builder=cb,
						classout=classout)
	print 'Summary=', summary
	return summary



def n_zero_cov_builder(d, N, modelchoice=None, trainingset_name=None,
			diagboost=Fudge):
	# ignore N
	assert modelchoice is None
	die.info('Mu_cov')
	assert len(d) > 0, "No data!"
	dim = d[0].value.shape[0]
	covlist = dictops.dict_of_X( lambda v: Num.array(v, Num.Float, copy=True),
					lambda acc, delta: Num.add(acc, delta, acc)
					)
	nlist = dictops.dict_of_accums()
	for x in d:
		nlist.add(x.classid, 1)
		covlist.add(x.classid, Num.outerproduct(x.value, x.value))

	for k in covlist.keys():
		# print 'k=', k
		Num.divide(covlist[k], nlist[k], covlist[k])
		# print 'Eigenval:a:', Num.LA.eigvalsh(covlist[k])

	boost_diag(covlist, diagboost*typ_trace(covlist))

	# We can't subtract the two inverse covariances here,
	# otherwise we mess up the calculation of logdet().

	models = {}
	for k in covlist.keys():
		models[k] = QCR.qmodel(Num.zeros((dim,), Num.Float),
					Num.LA.inv(covlist[k]),
					-logdet(covlist[k])
					)
	

	die.info('Mu_cov done')	
	return [ QCR.classifier('quadratic_class_model', models, trainingset_name=trainingset_name,
				uid=trainingset_name
				)
			]


def _droplist1(dim):
	return [ None ] + [ (i,) for i in range(dim) ]

def _droplist2s(dim):
	return [ None ] + [ (i,(i+1)%dim) for i in range(dim) ]

def _droplist2x(dim):
	return [ None ] + [ (i,j) for i in range(dim) for j in range(dim)]



def n_zero_cov_builder_drop(d, N, modelchoice=None, trainingset_name=None,
				diagboost=Fudge):
	"""Needs to return a list, not an iterator."""
	# ignore N
	assert modelchoice is None
	die.info('Mu_cov')
	assert len(d) > 0, "No data!"
	dim = d[0].value.shape[0]

	def _drop(v, droplist):
		tmp = Num.array(v, copy=True)
		if droplist is not None:
			for i in droplist:
				tmp[i] = 0.0
		return tmp

	typ_tr = None
	o = []
	global Droplist
	for drop in Droplist(dim):
		covlist = dictops.dict_of_X( lambda v: Num.array(v, Num.Float, copy=True),
						lambda acc, delta: Num.add(acc, delta, acc)
						)
		nlist = dictops.dict_of_accums()
		for x in d:
			nlist.add(x.classid, 1)
			xvtmp = _drop(x.value, drop)
			covlist.add(x.classid, Num.outerproduct(xvtmp, xvtmp))
	
		for k in covlist.keys():
			# print 'k=', k
			Num.divide(covlist[k], nlist[k], covlist[k])
			# print 'Eigenval:a:', Num.LA.eigvalsh(covlist[k])
	
		if typ_tr is None:
			# We need to boost the diagonal by the same amount
			# for each different dropped component, otherwise
			# the discriminants of the inverse covariance matrix
			# will be affected in bad ways.
			typ_tr = typ_trace(covlist)
		boost_diag(covlist, diagboost*typ_tr)
	
		# We can't subtract the two inverse covariances here,
		# otherwise we mess up the calculation of logdet().
	
		models = {}
		for k in covlist.keys():
			models[k] = QCR.qmodel(Num.zeros((dim,), Num.Float),
						Num.LA.inv(covlist[k]),
						-logdet(covlist[k])
						)
		
	
		tmp = QCR.classifier('quadratic_class_model', models,
						trainingset_name=trainingset_name,
				uid=hash((trainingset_name, drop))
				)
		tmp.add_info('drop_component', drop)
		o.append( tmp )
	return o



def n_mu_cov_builder(d, N, modelchoice=None, trainingset_name=None,
			diagboost=Fudge):
	# ignore N
	assert modelchoice is None
	die.info('Mu_cov')
	dim = d[0].value.shape[0]
	mulist = dictops.dict_of_X( lambda v: Num.array(v, Num.Float),
					lambda acc, delta: Num.add(acc, delta, acc)
					)
	covlist = dictops.dict_of_X( lambda v: Num.array(v, Num.Float),
					lambda acc, delta: Num.add(acc, delta, acc)
					)
	nlist = dictops.dict_of_accums()
	for x in d:
		nlist.add(x.classid, 1)
	for x in d:
		mulist.add(x.classid, x.value)
	for k in mulist.keys():
		Num.divide(mulist[k], nlist[k], mulist[k])
	mdof = dim
	die.info('Mu done')
	for x in d:
		tmp = x - mulist[x.classid]
		covlist.add(x.classid, Num.outerproduct(tmp, tmp))
	for k in mulist.keys():
		# print 'k=', k
		assert nlist[k] > mdof
		Num.divide(covlist[k], nlist[k]-mdof, covlist[k])
		# print 'Eigenval:a:', Num.LA.eigvalsh(covlist[k])

	for k in mulist.keys():
		# print 'k=', k
		Num.divide(covlist[k], nlist[k], covlist[k])
		# print 'Eigenval:a:', Num.LA.eigvalsh(covlist[k])

	boost_diag(covlist, diagboost)


	models = {}
	for k in mulist.keys():
		models[k] = QCR.qmodel(mulist[k],
					Num.LA.inv(covlist[k]),
					logdet(covlist[k])
					)
	

	die.info('Mu_cov done')	
	return [QCR.classifier('quadratic_class_model', models, trainingset_name=trainingset_name,
				uid=trainingset_name
				)
			]



def _test(dim=3, f=10, low=0.90, high=1.00, N=1000, u=False):
	import math
	if u:
		tmp1 = Num.RA.standard_normal((dim,dim))
		umat1, s, vt = Num.LA.svd( Num.dot(tmp1, Num.transpose(tmp1)) )
		tmp2 = Num.RA.standard_normal((dim,dim))
		umat2, s, vt = Num.LA.svd( Num.dot(tmp2, Num.transpose(tmp2)) )
	d = []
	for i in range(N):
		vector = Num.RA.standard_normal((dim,))
		if u:
			vector = Num.dot(vector, umat1)
		d.append( QCR.datum_tr(vector, 'a') )
	for i in range(N):
		vector = Num.RA.standard_normal((dim,))
		Num.multiply(vector,
				Num.exp((math.log(f)/dim)*(1+Num.arange(dim))),
				vector)
		if u:
			vector = Num.dot(vector, umat2)
		d.append( QCR.datum_tr(vector, 'b') )
	summary = _do_test(d, cb=Cb)
	assert low <= summary['Pcorrect'] <= high


def test1():
	_test(dim=3, f=10, low=0.90, high=1.00)
	_test(dim=3, f=0.1, low=0.90, high=1.00)
	_test(dim=6, f=30, low=0.97, high=1.00)
	_test(dim=3, f=1.0, low=0.30, high=0.70)
	_test(dim=6, f=30, low=0.97, high=1.00, u=True)
	_test(dim=9, f=10, low=0.97, high=1.00, u=True)
	_test(dim=9, f=0.1, low=0.97, high=1.00, u=True)
	_test(dim=2, f=1.0, low=0.30, high=0.70, u=True)
	_test(dim=12, f=1.0, low=0.30, high=0.70, u=True)
	_test(dim=1, f=2.0, low=0.60, high=0.85)
	_test(dim=1, f=1.5, low=0.50, high=0.8)
	_test(dim=1, f=2.5, low=0.60, high=0.85)
	_test(dim=1, f=3.5, low=0.65, high=0.90)
	_test(dim=1, f=5.0, low=0.75, high=0.96)

PSYCO = True

if __name__ == '__main__':
	import sys

	if PSYCO:
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass

	arglist = sys.argv[1:]
	Cb = n_zero_cov_builder
	cfd_file = 'classified.fiat'
	Droplist = _droplist1
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-coverage':
			COVERAGE = float(arglist.pop(0))
		elif arg == '-drop' or arg == '-drop1':
			Droplist = _droplist1
			Cb = n_zero_cov_builder_drop
		elif arg == '-drop2s':
			Droplist = _droplist2s
			Cb = n_zero_cov_builder_drop
		elif arg == '-drop2x':
			Droplist = _droplist2x
			Cb = n_zero_cov_builder_drop
		elif arg == '-nodetails':
			cfd_file = None
		elif arg == '-test':
			test1()
			sys.exit(0)
		elif arg == '-ftest':
			FTEST = float(arglist.pop(0))
			assert 0.0 < FTEST < 1.0
		else:
			die.die('Unrecognized argument: %s' % arg)
	go_auto(sys.stdin, coverage=COVERAGE, ftest=FTEST, cb=Cb,
			cfd_file = cfd_file)
