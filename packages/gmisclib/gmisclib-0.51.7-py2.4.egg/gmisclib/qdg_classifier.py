#!/usr/bin/env python

"""A quadratic classifier, but something about groups."""

import q_classifier_r as Q
import fiatio
import die
import g_closure
import qd_classifier as QD


N_PER_DIM = 6
COVERAGE = 3


def go_group_q(fd, n_per_dim = N_PER_DIM, ftrim=None,
		grouper=Q.default_grouper,
		evnm=None):
	d = Q.read_data(fd)

	classout = fiatio.writer(open('classified.fiat', 'w'))

	modelchoice = g_closure.Closure(QD.qd_classifier_desc, g_closure.NotYet,
					evaluator=Q.evaluator_from_name(evnm),
					ftrim=ftrim)
	classout.header('evaluator', evnm)
	classout.header('ftrim', ftrim)

	summary, out, wrong = Q.compute_group_class(
						d,
						modelchoice = modelchoice,
						n_per_dim = n_per_dim,
						builder=Q.forest_build,
						classout=classout,
						grouper=grouper)

	Q.default_writer(summary, out, classout, wrong)


def go_group_l(fd, n_per_dim = N_PER_DIM, ftrim=None,
		grouper=Q.default_grouper,
		evnm=None):
	import l_classifier
	d = Q.read_data(fd)

	classout = fiatio.writer(open('classified.fiat', 'w'))

	modelchoice = g_closure.Closure(l_classifier.l_classifier_desc, g_closure.NotYet,
					evaluator=Q.evaluator_from_name(evnm),
					ftrim=ftrim)
	classout.header('evaluator', evnm)
	classout.header('ftrim', ftrim)

	summary, out, wrong = Q.compute_group_class(
						d,
						modelchoice = modelchoice,
						n_per_dim = n_per_dim,
						builder=Q.forest_build,
						classout=classout,
						grouper=grouper)

	Q.default_writer(summary, out, classout, wrong)




if __name__ == '__main__':
	import sys

	try:
		import psyco
		psyco.full(memory=10000)
	except ImportError:
		pass

	arglist = sys.argv[1:]
	ftrim = None
	ct = 'Q'
	evnm = None
	while len(arglist)>0 and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-nperdim':
			N_PER_DIM = int(arglist.pop(0))
		elif arg == '-Q':
			ct = 'Q'
		elif arg == '-L':
			ct = 'L'
		elif arg == '-evaluator':
			evnm = arglist.pop(0)
		elif arg == '-c':
			trimf = float(arglist.pop(0))
			triml = float(arglist.pop(0))
			ftrim = (trimf, triml)
		elif arg == '-D':
			Q.D = 1
		else:
			die.die('Unrecognized argument: %s' % arg)
	assert len(arglist) == 0

	if ct == 'Q':
		go_group_q(sys.stdin, n_per_dim = N_PER_DIM, ftrim=ftrim, evnm=evnm)
	else:
		go_group_l(sys.stdin, n_per_dim = N_PER_DIM, ftrim=ftrim, evnm=evnm)
