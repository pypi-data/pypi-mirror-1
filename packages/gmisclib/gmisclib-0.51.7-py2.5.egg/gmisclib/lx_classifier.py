#!/usr/bin/env python

import l_classifier as L
import die
import q_classifier_r as Q
import fiatio


N_PER_DIM = 6



def go_cross(trfd, tsfd, n_per_dim = N_PER_DIM, ftrim=0.0):
	trd = Q.read_data(trfd)
	tsd = Q.read_data(tsfd)
	modelchoice = L.l_classifier_desc(trd+tsd, userank=1, ftrim=ftrim)
	classout = fiatio.writer(open('classified.fiat', 'w'))
	classout.header('userank', modelchoice.userank)
	classout.header('ftrim', modelchoice.ftrim)
	for (i, c) in enumerate(modelchoice.c):
		classout.header('Class%0d' % i, c)

	summary, out, wrong = Q.compute_cross_class(trd, tsd,
						modelchoice = modelchoice,
						n_per_dim = n_per_dim,
						builder=Q.forest_build,
						classout=classout)
	L.default_writer(summary, out, classout, wrong, modelchoice)



if __name__ == '__main__':
	import sys

	try:
		import psyco
		psyco.full(memory=10000)
	except ImportError:
		pass

	arglist = sys.argv[1:]
	ftrim = None
	while len(arglist)>0 and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-c':
			ftrim = float(arglist.pop(0))
		elif arg == '-nperdim':
			N_PER_DIM = int(arglist.pop(0))
		else:
			die.die('Unrecognized argument: %s' % arg)
	assert len(arglist) == 2
	trfd = open(arglist.pop(0), 'r')
	tsfd = open(arglist.pop(0), 'r')

	L.go_cross(trfd, tsfd, n_per_dim = N_PER_DIM, ftrim=ftrim)
