from gmisclib import Num
from gmisclib import mcmc
from gmisclib import die
from gmisclib import mcmc_helper
import gmisclib.multivariance_classes as MC
import gmisclib.multivariance_q as MQ
import gmisclib.multivariance_mm as MM



ERGCOVER = 3.0
HUGE = 1e30
				# -1 for a flat prior in inverse sigma,
				# 0 for somewhere in between





def _logp(prms, (x, modelchoice)):
	lp = 0.0
	p = modelchoice.unpack(prms)

	try:
		for x1 in x:
			lp += p.logp(x1)
	except MC.QuadraticNotNormalizable:
		return -HUGE

	return lp





def meanvar(dataset, N, modelchoice=MQ.quadratic):
	"""Given a dataset, this produces a bunch of MCMC estimates
	of plausible means and inverse covariance matrices for the dataset.
	Modelchoice is a particular size model, e.g. an instance of quadratic.
	The output is in the form [ (mean, inv_covar), ... ]."""
	assert N >= 0
	assert len(dataset)>0
	# print 'N=', N
	particular_model = modelchoice(dataset=dataset)
	startpack, varpack = particular_model.start(dataset)
	# print 'SPACK:', startpack
	# print 'VPACK:', varpack
	x = mcmc.bootstepper(_logp, startpack, varpack,
				c=(dataset,particular_model))
	# print 'X!'

	n = particular_model.ndim()
	# print 'ndim=', n
	mcmch = mcmc_helper.stepper(x)
	mcmch.run_to_bottom()
	# print 'bottom', N
	o = []
	for i in range(N):
		mcmch.run_to_ergodic(ERGCOVER/float(N))
		o.append( particular_model.unpack(x.prms()) )
	return o


def test_quadratic():
	d = []
	for l in sys.stdin:
		if l.startswith('#'):
			continue
		if l.strip() == '':
			continue
		a = Num.array( [float(s) for s in l.split()], Num.Float)
		d.append(a)
	for x in meanvar(d, 200, modelchoice=MQ.quadratic):
		print 'Mu:', x.mu
		print 'Inverse:', x.invsigma
		print


def test_diag_quadratic():
	d = []
	for l in sys.stdin:
		if l.startswith('#'):
			continue
		if l.strip() == '':
			continue
		a = Num.array( [float(s) for s in l.split()], Num.Float)
		d.append(a)
	for x in meanvar(d, 200, modelchoice=MQ.diag_quadratic):
		print 'Mu:', x.mu
		print 'Inverse:', x.invsigma
		print

def test_multimu():
	d = []
	for l in sys.stdin:
		if l.startswith('#'):
			continue
		if l.strip() == '':
			continue
		a = l.split()
		af = Num.array([float(s) for s in a[1:]], Num.Float)
		d.append(MM.datum_c(vector=af, classid=a[0]))
	for x in meanvar(d, 200, modelchoice=MM.multi_mu):
		print 'Inverse:', x.invsigma
		print 'Mu:', x.mu
		print


def test_multimu_diag():
	d = []
	for l in sys.stdin:
		if l.startswith('#'):
			continue
		if l.strip() == '':
			continue
		a = l.split()
		af = Num.array([float(s) for s in a[1:]], Num.Float)
		d.append(MM.datum_c(vector=af, classid=a[0]))
	for x in meanvar(d, 200, modelchoice=MM.multi_mu_diag):
		print 'Inverse:', x.invsigma
		print 'Mu:', x.mu
		print


FromName = {'quadratic' : MQ.quadratic, 'diag_quadratic': MQ.diag_quadratic,
		'multi_mu': MM.multi_mu, 'multi_mu_diag': MM.multi_mu_diag
	}

if __name__ == '__main__':
	import sys

	try:
		import psyco
		psyco.full(memory=10000)
	except ImportError:
		pass

	if len(sys.argv) <= 1:
		print 'Usage: multivariance model_name ...'
		print __doc__
		die.exit(0)
	if sys.argv[1] == 'quadratic':
		sys.argv = [sys.argv[0]] + sys.argv[2:]
		test_quadratic()
	elif sys.argv[1] == 'diag_quadratic':
		sys.argv = [sys.argv[0]] + sys.argv[2:]
		test_diag_quadratic()
	elif sys.argv[1] == 'multi_mu':
		sys.argv = [sys.argv[0]] + sys.argv[2:]
		test_multimu()
	elif sys.argv[1] == 'multi_mu_diag':
		sys.argv = [sys.argv[0]] + sys.argv[2:]
		test_multimu_diag()

