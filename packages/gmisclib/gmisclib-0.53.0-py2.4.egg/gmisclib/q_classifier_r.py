"""This is a support module, used by many types of classifiers."""

import Num
import types
import chunkio
import blue_data_selector
import math
import gpkavg
import die
import mcmc
import mcmc_helper
import g_implements
import fiatio
import random
import dictops
import gpkmisc

ERGCOVER = 4.0
D = 0
TGT = 0.01

class datum_c(object):
	__doc__ = """This is an unclassified datum, either in the
		test or training set."""

	__slots__ = ['value', 'uid']

	def __init__(self, vector, uid=None):
		"""Vector is the feature vector of this datum,
		and uid is an arbitrary identifier."""
		self.value = Num.asarray(vector, Num.Float)
		self.uid = uid

	def __str__(self):
		return "<datum_c fv=%s uid=%s>" % (str(self.value), self.uid)
	__repr__ = __str__


class datum_tr(datum_c):
	__doc__ = """This is a classified datum, presumably in
		the training set."""

	__slots__ = ['value', 'uid', 'classid']

	def __init__(self, vector, classid, uid=None):
		"""Vector is the feature vector of this datum,
		classid is the true class,
		and uid is an arbitrary identifier."""
		datum_c.__init__(self, vector, uid)
		self.classid = classid
	
	def __str__(self):
		return "<datum_tr class=%s fv=%s uid=%s>" % (self.classid,
								str(self.value),
								self.uid)
	__repr__ = __str__


class bluedata:
	__doc__ = """This is an extension of blue_data_selector.bluedata which
		is aware of the classids of data.  It tries to split the
		data evenly for each class."""

	def __init__(self, data, blueness = 2.0):
		self.ntot = 0
		per_class_data = dictops.dict_of_lists()
		for datum in data:
			per_class_data.add(datum.classid, datum)

		self.selector = {}
		for (cid, cldata) in per_class_data.items():
			self.ntot += len(cldata)
			self.selector[cid] = blue_data_selector.bluedata(cldata, blueness)
	

	def _chooseint(self, n):
		"""This chooses integers math.floor(n) or math.ceil(n) with
		appropriate probabilities so that the expectation value of
		_chooseint(n) is n.
		"""
		f = math.floor(n)
		p = n - f
		assert 0.0 <= p <= 1.0
		i = int(f)
		if random.random() < p:
			i += 1
		return i


	def split(self, n):
		frac = float(n)/float(self.ntot)
		npc = {}
		# First, we choose how many items to select from each class.
		while 1:
			# We pick random numbers for each class, then check to see if the
			# total is right.
			ntot = 0
			for (cid, selector) in self.selector.items():
				tmp = self._chooseint(frac*len(selector))
				assert tmp >= 0 and tmp <= len(selector)
				ntot += tmp
				npc[cid] = tmp
			if n-0.5 <= ntot <= n+0.5:
				break

		# Then, we use a blue data selector for each class to pick the right number
		# of items from that class.
		o1 = []
		o2 = []
		for (cid, selector) in self.selector.items():
			t1, t2 = selector.split(npc[cid])
			o1.extend( t1 )
			o2.extend( t2 )
		assert len(o1) == ntot
		# Finally, we shuffle the classes back together.
		random.shuffle(o1)
		random.shuffle(o2)
		# ...and return.
		return (o1, o2)

	
	def __len__(self):
		return self.ntot



def _r1if(delta):
	return 0.5*(1.0 - delta/math.hypot(delta, 1.0))




def prior(training, testing):
	"""This assumes that you choose class C
	with probability 1 if P(C) is the
	biggest among all the classes.
	It is the best strategy, assuming you can't
	see the feature vector.
	"""
	dtr = dictops.dict_of_accums()
	for datum in training:
		dtr.add(datum.classid, 1)

	counts_best = 0.0
	kbest = None
	for (k, counts) in dtr.items():
		if counts > counts_best:
			counts_best = counts
			kbest = k

	chance = 0
	for datum in testing:
		if datum.classid == kbest:
			chance += 1
	return chance/float(len(testing))



def max_correct(training, testing):
	"""This is a hard, conservative upper limit
	for the probability of correct classification.

	One cannot hope to classify an item correctly,
	if the item's class is not represented
	in the training set.

	If the class is present in the training
	set but not in the test set, then what happens?
	It could be buried among items from other classes,
	in which case it wouldn't lead to any false
	predictions.  Consequently, absences from the
	test set doesn't hurt the maximum possible
	classification probability.
	"""
	dtr = dictops.dict_of_accums()
	for datum in training:
		dtr.add(datum.classid, 1)

	impossible = 0
	for datum in testing:
		if not datum.classid in dtr:
			impossible += 1

	return float(len(testing)-impossible)/float(len(testing))






def _addwrongD(wrong, failures):
	for (k, v) in failures.iteritems():
		wrong.add(k, v)


def _addwrong(wrong, failures):
	for t in failures:
		wrong.add(t, 1)


def _doclass(qc, testing, verbose=True):
	"""testing is a list of data.
	qc is a classifier.
	This classifies the data and yields a list of dictionaries,
	each of which contains a bunch of results and information.
	"""
	info = qc.info.copy()
	for datum in testing:
		P = qc.P(datum)
		tmp = info.copy()

		# It is tempting to use qc.bestc() here, but
		# not a good idea, as it would involve calculating
		# log(P) twice, and that can be expensive.
		bestcl = None
		bestp = 0.0
		for (cl, p) in P:
			if p > bestp:
				bestp = p
				bestcl = cl
		tmp['compclass'] = bestcl

		if datum.uid is not None:
			tmp['Duid'] = datum.uid

		if verbose:
			tmp['V'] = chunkio.chunkstring_w().write_NumArray(datum.value, str).close()
			tmp['P'] = chunkio.chunkstring_w().write_dict(dict(P)).close()
		try:
			tmp['trueclass'] = datum.classid
		except AttributeError:
			pass
		yield tmp




def read_data(fd, commentarray=None):
	"""Reads in feature vectors where the first element is the true class."""
	d = []
	len_a = None
	# die.info('Reading')
	print '# Reading'
	ln = 0
	for l in fd:
		ln += 1
		if l.startswith('#'):
			if commentarray is not None:
				commentarray.append(l[1:])
			continue
		aa = l.split('#', 1)
		if len(aa) > 1:
			uid = aa[1].strip()
		else:
			uid = 'Line:%d' % ln
		a = aa[0].split()
		if len(a) != len_a:
			if len_a is None:
				len_a = len(a)
			else:
				die.die('Not all vectors have length=%d.  Problem on line %d'
						% (len_a-1, ln)
					)
		d.append( datum_tr(Num.array([float(x) for x in a[1:]]),
				a[0], uid)
				)
	return d


def get_dim(fd):
	"""This function takes a list of data (type datum_tr)
	and makes sure that they all have the same length feature
	vector.  If so, it reports the length (dimension) of the
	feature vector.
	"""
	assert type(fd) == types.ListType
	dim = None
	for x in fd:
		assert isinstance(x, datum_tr)
		if len(x.value) != dim:
			if dim is None:
				dim = len(x.value)
			assert len(x.value) == dim
	return dim
		


def compute_cross_class(training, testing,
			modelchoice=None, n_per_dim=None,
			builder=None, classout=None,
			trainingset_name = None,
			verbose=True):
	"""Build classifiers based on the training set,
	and test them on the testing set.
	Modelchoice here is the completed class object,
	not a closure."""

	if len(training) == 0:
		die.die('No training data.')
	if len(testing) == 0:
		die.die('No data to classify.')

	dim = get_dim(training)
	assert get_dim(testing) == dim
	if dim <= 0:
		die.die('zero dimensional data')

	nok = 0
	total = 0
	wrong = dictops.dict_of_accums()
	k = None

	priorchance = prior(training, testing)
	maxcorrect = max_correct(training, testing)
	classifiers = builder(training, n_per_dim*dim,
				modelchoice=modelchoice,
				trainingset_name=trainingset_name)
	for qc in classifiers:
		failures = qc.list_wrong_classifications(testing)
		qc.add_info('correct', len(testing)-len(failures))
		qc.add_info('Ntests', len(testing))
		_addwrong(wrong, failures)
		if classout is not None:
			classout.extend( _doclass(qc, testing, verbose=verbose) )
		nok += len(failures)
		total += len(testing)
	pcorrect = float(total-nok)/float(total)

	if priorchance < maxcorrect:
		k = (pcorrect-priorchance)/(maxcorrect-priorchance)
	print '#NOK=', nok, total, float(nok)/total

	summary = {'nok': nok, 'total': total,
			'Pcorrect': float(total-nok)/float(total),
			'Chance': priorchance,
			'Pperfect': maxcorrect
			}
	if k is not None:
		summary['K'] = k

	return (summary, classifiers, wrong)



def compute_self_class(d, coverage=None, ftest=None,
		modelchoice=None, n_per_dim=None,
		builder=None, classout=None, verbose=True):

	"""modelchoice here is expected to take one argument-- the data."""

	dim = get_dim(d)

	if dim <= 0:
		die.die('zero dimensional data')
	if len(d) == 0:
		die.die('No data to classify.')
	Ntry = int(round(coverage/ftest))
	bdata = bluedata(d)
	nok = 0; total = 0;
	wrong = dictops.dict_of_accums()
	out = []; k = []; pch = []; pmx = []; pcrct = []
	for tr in range(Ntry):
		print '# Building'
		testing, training = bdata.split(ftest*len(bdata))

		# Modelchoice is a closure, and evaluation happens here:
		if modelchoice is not None:
			c_modelchoice = modelchoice(training)
		else:
			c_modelchoice = None
		tsum, classifiers, twr = compute_cross_class(training, testing, c_modelchoice,
							n_per_dim, builder, classout,
							trainingset_name = tr,
							verbose=verbose
							)

		pmx.append( tsum['Pperfect'] )
		pch.append( tsum['Chance'] )
		total += tsum['total']
		nok += tsum['nok']
		pcrct.append( 1.0-float(tsum['nok'])/tsum['total'] )
		_addwrongD(wrong, twr)
		out.extend(classifiers)
		if 'K' in tsum:
			k.append( tsum['K'] )

	summary = {'nok': nok, 'total': total}

	try:
		summary['K'], ksigma = gpkavg.avg(k, None, 0.0001)
		summary['KSigma'] = ksigma
	except ValueError, x:
		die.info('%s: K' % str(x))

	try:
		summary['Chance'], chsigma = gpkavg.avg(pch, None, 0.0001)
		summary['ChSigma'] = chsigma
	except ValueError, x:
		die.info('%s: PChance' % str(x))
	try:
		summary['Perfection'], prfsigma = gpkavg.avg(pmx, None, 0.0001)
		summary['PerfectionSigma'] = prfsigma
	except ValueError, x:
		die.info('%s: Pperfect' % str(x))

	try:
		summary['Pcorrect'], psigma = gpkavg.avg(pcrct, None, 0.0001)
		summary['PSigma'] = psigma
	except ValueError, x:
		die.info('%s: Pcorrect' % str(x))


	return (summary, out, wrong)





def default_grouper(x):
	return x.uid.split('/')[0]


def group_data(d, gr):
	o = dictops.dict_of_lists()
	for t in d:
		o.add(gr(t), t)
	return o




def compute_group_class(dg, modelchoice=None, n_per_dim=None,
		builder=None, classout=None,
		grouper=default_grouper,
		verbose=True):
	"""This function makes sure that the training set and testing set
	come from different groups.   The 'grouper' returns a group
	name, when given a datum.   Modelchoice is expected to take
	one argument, the training set.
	"""

	dim = get_dim(dg)

	if dim <= 0:
		die.die('zero dimensional data')
	if len(dg) == 0:
		die.die('No data to classify.')

	nok = 0; total = 0;
	wrong = dictops.dict_of_lists()
	out = []; k = []; pch = []; pcrct = []; pmx = []
	groups = group_data(dg, grouper)
	for (tgn, testing) in groups.items():
		training = []
		for (tmpgn, tmpg) in groups.items():
			if tmpgn != tgn:
				training.extend( tmpg )
		print '# Building'

		# Modelchoice is a closure, and evaluation happens here:
		if modelchoice is not None:
			c_modelchoice = modelchoice(training)
		else:
			c_modelchoice = None
		tsum, classifiers, twr = compute_cross_class(training, testing,
							c_modelchoice, n_per_dim,
							builder, classout,
							trainingset_name = tgn,
							verbose=verbose
							)

		pmx.append( tsum['Pperfect'] )
		pch.append( tsum['Chance'] )
		total += tsum['total']
		nok += tsum['nok']
		pcrct.append( 1.0-float(tsum['nok'])/tsum['total'] )
		_addwrongD(wrong, twr)
		out.extend(classifiers)
		if 'K' in tsum:
			k.append( tsum['K'] )

	summary = {'nok': nok, 'total': total}

	try:
		summary['K'], ksigma = gpkavg.avg(k, None, 0.0001)
		summary['KSigma'] = ksigma
	except ValueError, x:
		die.info('%s: K' % str(x))

	try:
		summary['Chance'], chsigma = gpkavg.avg(pch, None, 0.0001)
		summary['ChSigma'] = chsigma
	except ValueError, x:
		die.info('%s: PChance' % str(x))
	try:
		summary['Perfection'], prfsigma = gpkavg.avg(pmx, None, 0.0001)
		summary['PerfectionSigma'] = prfsigma
	except ValueError, x:
		die.info('%s: Pperfect' % str(x))

	try:
		summary['Pcorrect'], psigma = gpkavg.avg(pcrct, None, 0.0001)
		summary['PSigma'] = psigma
	except ValueError, x:
		die.info('%s: Pcorrect' % str(x))

	return (summary, out, wrong)





class model_template(object):
	# def __init__(self):
		# pass
	# __init__.g_implements = g_implements.varargs
	# __slots__ = []

	def logp(self, datum):
		pass


class qmodel(object):
	__slots__ = ['_mu', '_invsigma', '_bias']

	def __init__(self, mu, invsigma, offset):
			# Copy the data, so there is no risk of
			# it changing underneath you...
		self._mu = Num.array(mu, Num.Float, copy=True)
		self._invsigma = Num.array(invsigma, Num.Float, copy=True)
		assert len(self._mu.shape) == 1
		assert self._invsigma.shape == (self._mu.shape * 2), "Shapes must match: %s vs %s" % (str(self._invsigma.shape), str(self._mu.shape))
		# The above is a duplication of a tuple, not multiplication.
		self._bias = offset

	def logp(self, datum):
		delta = datum - self._mu
		parab = gpkmisc.qform(delta, self._invsigma)
		return -parab/2.0 + self._bias

	def mu(self):
		return self._mu

	def invsigma(self):
		return self._invsigma

	def bias(self):
		return self._bias

	def tochunk(self, chunkwriter):
		chunkwriter.groupstart('quadratic_class_model', b=1 )
		chunkwriter.comment('Offset:')
		chunkwriter.write_float(self.bias())
		chunkwriter.comment('Mu:')
		chunkwriter.write_NumArray(self.mu(), b=1)
		chunkwriter.comment('Inverse(covariance):')
		chunkwriter.write_NumArray(self.invsigma(), b=1)
		chunkwriter.groupend()



	def __str__(self):
		return '<model: mu=%s invsigma=%s bias=%g>' % (
				str(self.mu()), str(self.invsigma()),
				self.bias())


def _qmodel_fromchunk(chunk):
	"""This the inverse of qmodel.tochunk(),
	except the group start is already read.
	"""
	offset = chunk.read_float()
	mu = chunk.read_NumArray()
	if len(mu.shape) != 1:
		raise chunkio.BadFileFormat, 'mu must be 1-d array'
	invsigma = chunk.read_NumArray()
	if len(invsigma.shape) != 2:
		raise chunkio.BadFileFormat, 'invsigma must be 1-d array'
	if invsigma.shape != mu.shape*2:
		raise chunkio.BadFileFormat, 'sizes do not match'
	return qmodel(mu, invsigma, offset)


def _lmodel_fromchunk(chunk):
	"""This the inverse of lmodel.tochunk(),
	except the group start is already read.
	"""
	offset = chunk.read_float()
	direction = chunk.read_NumArray()
	if len(direction.shape) != 1:
		raise chunkio.BadFileFormat, 'direction must be 1-d array'
	ref = chunk.read_NumArray()
	if len(direction.shape) != 1:
		raise chunkio.BadFileFormat, 'reference_point must be 1-d array'
	if direction.shape != ref.shape:
		raise chunkio.BadFileFormat, 'sizes do not match'
	return lmodel(direction, offset, ref)


def model_fromchunk(chunk):
	"""A factory function to read in an arbitrary classifier model."""
	tmp = chunk.groupstart()
	if tmp == 'quadratic_class_model':
		rv = _qmodel_fromchunk(chunk)
	elif tmp == 'linear_class_description':
		rv = _lmodel_fromchunk(chunk)
	else:
		raise chunkio.BadFileFormat, 'Unknown type of classifier model: %s' % tmp
	chunk.groupend()
	return rv


_qzmodel_cache = {}
def qzmodel(ndim):
	global _qzmodel_cache
	if ndim in _qzmodel_cache:
		return _qzmodel_cache[ndim]
	zmu = Num.zeros((ndim,), Num.Float)
	zis = Num.zeros((ndim, ndim), Num.Float)
	zm = qmodel(zmu, zis, 0.0)
	if len(_qzmodel_cache) > 20:
		_qzmodel_cache.popitem()
	_qzmodel_cache[ndim] = zm
	return zm




class lmodel(object):
	__slots__ = ['direction', 'bias', 'reference']

	def __init__(self, direction, offset, reference_pt):
			# Copy direction, so no chance of it changing
			# due to external causes...
		self.direction = Num.array(direction, Num.Float, copy=True)
		self.bias = offset
		self.reference = reference_pt

	def logp(self, datum):
		# print "\t bias=", self.bias
		# print "\tdir=", self.direction
		# print "\tdatum=", datum
		# print "\treference=", self.reference
		# print '\to=', self.bias+Num.dot(datum-self.reference, self.direction)
		return self.bias + Num.dot(datum-self.reference, self.direction)

	def __str__(self):
		return '<model: %s ref=%s bias=%g>' % (str(self.direction), str(self.reference), self.bias)

	def tochunk(self, chunkwriter):
		chunkwriter.groupstart('linear_class_description', b=1 )
		chunkwriter.comment('Offset:')
		chunkwriter.write_float(self.bias)
		chunkwriter.comment('dir:')
		chunkwriter.write_NumArray(self.direction, b=1)
		chunkwriter.comment('reference_pt:')
		chunkwriter.write_NumArray(self.reference, b=1)
		chunkwriter.groupend()



_lzmodel_cache = {}
def lzmodel(ndim):
	if ndim in _lzmodel_cache:
		return _lzmodel_cache[ndim]
	z = Num.zeros((ndim,), Num.Float)
	zm = lmodel(z, 0.0, z)
	if len(_lzmodel_cache) > 50:
		_lzmodel_cache.popitem()
	_lzmodel_cache[ndim] = zm
	return zm




class classifier_desc(object):
	def __init__(self, list_of_classes, fvdim, evaluator=None, ftrim=None):
		assert type(fvdim) == types.IntType
		assert fvdim > 0
		self.ndim = fvdim

		# Make sure that list_of_classes is iterable
		self.c = list(list_of_classes)

		self.nc = len(self.c)
		self.evaluator = evaluator
		self.ftrim = ftrim
		self.cmap = {}
		for (i, c) in enumerate(self.c):
			self.cmap[c] = i

	def np(self):
		"""The number of parameters required to define one class."""
		raise RuntimeError, "Virtual Function."

	def npt(self):
		"""The number of parameters required to define the classifier."""
		raise RuntimeError, "Virtual Function."

	def unpack(self, prmvec, trainingset_name=None, uid=None):
		"""Produce a classifier from a parameter vector."""
		raise RuntimeError, "Virtual Function."

	def start(self, data):
		"""Starting position for Markov Chain Monte Carlo."""
		raise RuntimeError, "Virtual Function."

	def __str__(self):
		return "<classifier_desc: ndim=%d nc=%d cmap=%s>" % (self.ndim, self.nc, self.cmap)
	__repr__ = __str__


def _logp(x, (data, cdesc)):
	assert isinstance(cdesc, classifier_desc)
	cl = cdesc.unpack(x)
	assert isinstance(cl, classifier)
	o1 = evaluate_Bayes(cl, data)
	# The following little term prevents infinitely  strong
	# classifiers, in case the classes are completely
	# seperable.   Basically, it's there to prevent
	# overflows.
	o = -o1 - (TGT/o1)
	if D:
		print 'cl=', cl, 'o=', o1, o
	return o



def forest_build(data, N, modelchoice=None, trainingset_name=None):
	start, V = modelchoice.start(data)
	x = mcmc.bootstepper(_logp, start, V, c=(data, modelchoice))
	mcmch = mcmc_helper.stepper(x)
	nsteps = mcmch.run_to_bottom()
	if nsteps > 100:
		print '#NSTEPS:', nsteps
	o = []
	for i in range(N):
		mcmch.run_to_ergodic(ERGCOVER/float(N))
		tmp = modelchoice.unpack( x.current().prms(),
					trainingset_name=trainingset_name,
					uid=hash((trainingset_name,i)) )
		o.append( (tmp.evaluate(data), tmp) )
	o.sort()
	m = int(round(math.sqrt(N)))
	return [ cl for (evaluation,cl) in o[:m] ]



class classifier(object):
	def __init__(self, typename, models, info = None,
			trainingset_name=None, uid=None):
		self.typename = typename
		assert type(models) == types.DictType
		self.class_models = models
		# Info is not part of the internal operation of the classifier,
		# but it is stuff that is important to write out.
		if info is not None:
			self.info = info.copy()
		else:
			self.info = {}
		self.info['trainingset'] = trainingset_name
		self.info['Cuid'] = uid


	def add_model(self, classname, model):
		"""Add a class to an existing classifier."""
		g_implements.check(model, model_template)
		assert type(classname) == types.StringType
		self.class_models[classname] = model


	def list_classes(self):
		return self.class_models.keys()


	def add_info(self, k, v):
		self.info[k] = v

	def P(self, datum, whichclass=None):
		"""Determine the probability of being in each class.
		If whichclass=None, then it returns a list of
		tuples [(classname,P), ...] for all classes.
		Otherwise, it returns the probability of the
		desired class.
		"""
		EXPLIM = -30
		HUGE = 1e30
		lP = []
		cnames = self.class_models.keys()
		# print "Datum=", datum
		bgst = -HUGE
		for qp in self.class_models.itervalues():
			tmp = qp.logp(datum.value)
			lP.append(tmp)
			if tmp > bgst:
				bgst = tmp
		Psum = 0.0
		P = []
		for lp in lP:
			tmp = math.exp(max(lp-bgst, EXPLIM))
			P.append( tmp )
			Psum += tmp
		if whichclass is None:
			return [(cn,P/Psum) for (cn,P) in zip(cnames, P) ]
		return P[cnames.index(whichclass)]/Psum


	def bestc(self, datum):
		"""Determine the best class for a datum."""
		HUGE = 1e30
		# print "Datum=", datum
		bgst = -HUGE
		bgc = None
		for (c, qp) in self.class_models.iteritems():
			tmp = qp.logp(datum.value)
			if tmp > bgst:
				bgst = tmp
				bgc = c
		return bgc


	def __str__(self):
		o = [ '<classifier:' ]
		for (c, q) in self.class_models.items():
			o.append('%s: %s' % (c, str(q)))
		o.append( '>' )
		return '\n'.join(o)

	__repr__ = __str__


	def list_wrong_classifications(self, classdata):
		nok = []
		for datum in classdata:
			bestc = self.bestc(datum)
			if bestc != datum.classid:
				nok.append(datum.uid)
		return nok




	def writer(self, dcw):
		dcw.groupstart(self.typename)
		dcw.comment('Classifier:')
		dcw.write_dict_of(self.class_models,
				lambda dcw, ac: ac.tochunk(dcw), b=1)
		info = self.info.copy()
		dcw.write_dict(info)
		dcw.groupend()


def read_classifier(chunk):
	typename = chunk.groupstart()
	models = chunk.read_dict_of(model_fromchunk)
	info = chunk.read_dict(str)
	chunk.groupend()
	return classifier(typename, models, info=info,
			trainingset_name=info.get('trainingset', None),
			uid=info.get('Cuid', None)
			)


class forest_mixin(object):
	def __init__(self, cdesc):
		self.cdesc = cdesc

	def evaluate(self, data):
		if self.cdesc.evaluator is None:
			return evaluate_Bayes(self, data)
		return self.cdesc.evaluator(self, data)


def evaluate_match(self, data):
	"""This can be passed into a classifier descriptor as
	the evaluate argument.
	It returns the number of exact matches between the classified
	data and the input, true classification.
	"""
	# print 'classifer=', self
	o = 0
	for datum in data:
		sbc = self.bestc(datum)
		# print 'sbc(', datum, ')=', sbc, 'dc=', datum.classid, 'P=', self.P(datum)
		if sbc != datum.classid:
			o += 1
	return o



class evaluate_match_w_rare:
	__doc__ = """This is called in the same way as evaluate_match
		or evaluate_Bayes.  It pretends to be a function,
		except that you can weight the values of different
		classes when you construct the class.
		"""
	__name__ = 'evaluate_match_w_rare'

	def __init__(self):
		self.weights = None
	
	def _compute_weights(self, data):
		classcounts = dictops.dict_of_accums()
		for datum in data:
			classcounts.add(datum.classid, 1)

		ctotal = 0
		for counts in classcounts.values():
			ctotal += counts
		ctotal = float(ctotal)
		weights = {}
		for (classname, counts) in classcounts.items():
			weights[classname] = -math.log(float(counts)/ctotal)
		return weights
	

	def __call__(self, clssfr, data):
		if self.weights is None:
			self.weights = self._compute_weights(data)

		o = 0
		for datum in data:
			if clssfr.bestc(datum) != datum.classid:
				o += self.weights[datum.classid]
		return o




def evaluate_Bayes(self, data):
	"""Below, we assume that some of the
	data in each class are dubious, and should
	be ignored if they are sufficiently improbable.
	We modify the probability scores of data that is
	among the worst (self.cdesc.ftrim[0] fraction),
	and limit those scores to be no larger than
	self.cdesc.ftrim[1] larger than the best score.
	This lets you limit by score or limit by fraction
	or any mixture in between.   If self.cdesc.ftrim is None,
	then no limiting or trimming is done.
	"""
	if self.cdesc.ftrim is None:
		o = 0.0
		for datum in data:
			o -= math.log(self.P(datum, datum.classid))
		return o
	# Below, we assume a fraction trimfrac of the
	# data in each class are dubious, and should
	# be ignored if they are sufficiently improbable.
	trimfrac, trimlevel = self.cdesc.ftrim
	assert trimfrac>=0 and trimfrac<=1.0
	o = dictops.dict_of_lists()
	for datum in data:
		sb = -math.log(self.P(datum, datum.classid))
		assert isinstance(datum, datum_tr), "Use ftrim only with training set!"
		o.add(datum.classid, sb)
	oo = 0.0
	for classid, scorelist in o.items():
		scorelist.sort()
		n = int(round((1.0-trimfrac)*(len(scorelist)-1)))
		for t1 in scorelist[:n]:
			oo += t1
		tcut = scorelist[0] + trimlevel
		for t2 in scorelist[n:]:
			if D and t1 < t2:
				print 'Trimming %g %g in %s:%s' % (t1, t2, classid, scorelist)
			oo += min(tcut, t2)
	return oo


def classifier_writer(dcw, a_classifier):
	a_classifier.writer(dcw)



def default_writer(summary, out, classout, wrong):
	"""Out needs to be a list, not an iterator, because we use it twice."""

	dc = chunkio.datachunk_w( open("classes.chunk", "w") )
	dc.comment('Header:')
	header = summary.copy()
	ctype = None
	for cl in out:
		if ctype is None:
			ctype = cl.typename
		else:
			assert cl.typename == ctype, 'Cannot handle mixtures of different classifiers.'
	header['classifier_type'] = ctype
	dc.write_dict( header )
	dc.comment('classifiers:')
	dc.write_array_of(out, classifier_writer, b=1)
	out = None
	dc = None
	for (uid, nfailures) in wrong.items():
		print 'WRONG', nfailures, summary['total'], uid



def list_classes(data):
	"""List the names of the classes in a dataset,
	with the most populus classes first.
	"""
	cids = dictops.dict_of_accums()
	for datum in data:
		assert type(datum.classid) == types.StringType
		cids.add(datum.classid, 1)

	cn = [(-n, cid) for (cid, n) in cids.items() ]
	cn.sort()
	return [ cid for (n, cid) in cn ]




def read_fiat(fd):
	h, d, c = fiatio.read(fd)
	for t in d:
		if 'V' in t:
			t['V'] = chunkio.stringchunk(t['V']).read_NumArray()
		if 'P' in t:
			t['P'] = chunkio.stringchunk(t['P']).read_dict(float)
	return (h, d, c)



def name_of_evaluator(e):
	"""Used to get the name of an evaluator, to write it
	to a file header.
	"""
	if e is None:
		return evaluate_Bayes.__name__
	elif hasattr(e, '__name__'):
		return e.__name__
	else:
		return str(e)



def evaluator_from_name(nm):
	if nm is None or nm == 'Bayes' or nm == 'evaluate_Bayes':
		return evaluate_Bayes
	elif nm == 'match' or nm == 'evaluate_match':
		return evaluate_match
	elif nm == 'match_w_rare' or nm == 'evaluate_match_w_rare':
		return evaluate_match_w_rare()
	else:
		die.die('Bad name for evaluator: %s' % nm)
