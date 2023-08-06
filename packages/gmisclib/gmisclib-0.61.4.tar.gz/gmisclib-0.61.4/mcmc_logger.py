from gmisclib import mcmc_helper as mcmcP
# from newstem2 import newlogger as LG

class logger_c(mcmcP.logger_template):
	"""This class is called from the Markov-Chain stepper
	and writes the log file.
	"""
	def __init__(self, logwriter, iterstep=100, ergstep=0.1):
		assert iterstep >= 0
		assert ergstep >= 0.0
		# self.lg = LG.logger(fd)
		self.lg = logwriter
		self.iterstep = iterstep
		self.ergstep = ergstep
		# self.__g_implements__ = ['logger_template']
		self.nlogged = 0
		self.erg = 0.0
		self.last_add_iter = 0
		self.last_logged_erg = None
		self.last_logged_iter = None
		self.best = None
		self.reason = 'sampled'


	def set_logstep(self, iterstep, ergstep, reason='sampled'):
		self.reason = reason
		assert iterstep > 0
		self.iterstep = iterstep
		if ergstep is None:
			self.ergstep = 0.0
		else:
			assert ergstep >= 0.0
			self.ergstep = ergstep
		self.lg.flush()


	def add(self, stepperInstance, iter):
		"""Called every step: this decides whether
		data should be logged.
		"""
		self.erg += stepperInstance.ergodic() * (iter-self.last_add_iter)
		self.last_add_iter = iter
		reason = []
		if(self.last_logged_iter is None or self.last_logged_erg is None):
			reason.append('initial')
		elif(iter>self.last_logged_iter+self.iterstep
			and self.erg>self.last_logged_erg+self.ergstep
			):
			reason.append(self.reason)
		elif self.best is None or stepperInstance.current().logp_nocompute()>self.best:
			self.best = stepperInstance.current().logp_nocompute()
			reason.append('best')
		if reason:
			self.Add(stepperInstance, iter, reason=','.join(reason))


	def Add(self, stepperInstance, iter, reason=None):
		"""Actually write a set of parameters into the log file."""
		print 'Logging', stepperInstance.current().logp_nocompute(), 'iter=', iter
		self.nlogged += 1
		self.last_logged_erg = self.erg
		self.last_logged_iter = iter
		self.lg.add('UID', stepperInstance.current().prms(),
				stepperInstance.current().pd.idxr.map,
				stepperInstance.current().logp(),
				iter,
				extra={'T': stepperInstance.acceptable.T(),
					'resetid': stepperInstance.reset_id(),
					},
				reason=reason
				)
		self.lg.flush()


	def close(self):
		self.lg.close()

	def comment(self, comment):
		self.lg.comment(comment)
		self.lg.flush()

	def header(self, k, v):
		self.lg.header(k, v)

	def headers(self, hdict):
		self.lg.headers(hdict)

	def reset(self):
		self.nlogged = 0
		self.erg = 0.0
		self.last_logged_erg = None
		self.comment("Reset")


	def set_trigger_point(self):
		self.nlogged = 0
		self.erg = 0.0
		self.last_logged_erg = None
		self.comment("run_to_bottom finished")

