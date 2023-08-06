"""Subroutines for q_classifier.py that implement a multi-mu model.
That is, one where all the classes share a common covariance matrix.
"""

import math
import multivariance as M
import q_classifier as QC
from gmisclib import dictops

HUGE = 1e30

def count_the_classes(data):
	"""How many examples of each class do we have?"""
	counts = {}
	for datum in data:
		dictops.add_doc(counts, datum.classid, 1)
	return counts



def build_classifiers(data, N, modelchoice=M.multi_mu):
	"""Builds a set of quadratic classifiers.
	Data is a list of datum_tr .
	It returns a list: [ (evaluation_result, classifier_description), ... ] ."""

	assert modelchoice==M.multi_mu or modelchoice==M.multi_mu_diag

	cprms = M.meanvar(data, N, modelchoice)
	assert isinstance(cprms[0], M.multi_mu_with_numbers)	\
		or isinstance(cprms[0], M.multi_mu_diag_with_numbers)

	classlist = cprms[0].desc.int_to_id.values()

	if modelchoice==M.multi_mu_diag:
		details = M.diag_quadratic(ndim=cprms[0].desc.ndim())
	elif modelchoice==M.multi_mu:
		details = M.quadratic(ndim=cprms[0].desc.ndim())
	else:
		RuntimeError, 'Cannot happen'

	classcounts = count_the_classes(data)
	# Now, we build a bunch of classifiers
	classifiers = []
	for tmp in cprms:
		qc = QC.classifier()
		for c in classlist:
			# Bias is the Bayesean prior: classes with more training examples
			# are more likely.
			bias = math.log(classcounts[c])
			if modelchoice==M.multi_mu_diag:
				q = M.diag_quadratic_with_numbers(tmp.mu[c], tmp.invsigma, \
										details, bias)
			elif modelchoice==M.multi_mu:
				q = M.quadratic_with_numbers(tmp.mu[c], tmp.invsigma,
										details, bias)
			else:
				RuntimeError, 'Cannot happen'
			qc.addQuad(c, q)
		classifiers.append(qc)
	return classifiers

