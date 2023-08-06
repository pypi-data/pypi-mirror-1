"""Implements the creation of quadratic and diagonal quadratic
classifiers for q_classifier.py.
"""



import multivariance
import math
import q_classifier as QC
import random

HUGE=1e30

def build_classifiers(data, N, modelchoice=multivariance.quadratic):
	"""Builds a set of quadratic classifiers.
	Data is a list of datum_tr .
	It returns a list:
		[ (evaluation_result, classifier_description), ... ] .
	"""
	assert modelchoice==multivariance.quadratic	\
		or modelchoice==multivariance.diag_quadratic
	dcl = {}
	for datum in data:
		try:
			dcl[datum.classid].append(datum.value)
		except KeyError:
			dcl[datum.classid] = [ datum.value ]
	ncl = len(dcl)
	# print '# ncl=', ncl
	# nvar = 1 + int(math.ceil(math.sqrt(N)))
	nvar = 1 + int(math.ceil( min(float(3*N)**(1.0/len(dcl)), math.sqrt(N)) ))
	cprms = {}
	for (c, cd) in dcl.items():
		print '# Multivar on %s' % c
		cprmcl = multivariance.meanvar(cd, nvar, modelchoice)

		# This is effectively the Bayesean prior: classes where we have
		# seen lots of examples are more probable.
		for cprmc in cprmcl:
			cprmc.bias = math.log(len(cd))
		cprms[c] = cprmcl
		# print '\t cprmcl:', cprmcl

		assert len(cprms[c]) > 0

	classifiers = []
	# Now, we build a bunch of classifiers
	for i in range(N):
		qc = QC.classifier()
		assert len(qc.class_models) == 0
		# For each class, choose one plausible description:
		for (c, cpa) in cprms.items():
			# print 'C=', c, 'cpa=', cpa
			assert len(cpa)>1
			qc.addQuad(c, random.choice(cpa))
			# print 'qc=', qc
		classifiers.append(qc)
	# print 'classifiers=', classifiers
	return classifiers
