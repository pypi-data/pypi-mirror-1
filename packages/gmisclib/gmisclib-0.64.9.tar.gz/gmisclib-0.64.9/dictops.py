"""Operations on dictionaries."""


__version__ = "$Revision: 1.9 $"

def filter(d, l):
	"""Passes through items listed in l.
	@param l: list of keys to preserve
	@type l: list
	@param d: dictionary to copy/modify.
	@type d: mapping
	@return: a dictionary where all keys not listed in l are removed;
		all entries not listed in l are copied into the (new)
		output dictionary.
	@rtype: dict
	"""
	o = {}
	for t in l:
		o[t] = d[t]
	return o


def remove(d, l):
	"""Removes items listed in l.
	@param l: list of keys to remove
	@type l: list
	@param d: dictionary to copy/modify.
	@type d: mapping
	@return: a dictionary where all keys listed in l are removed;
		all entries not listed in l are copied into the (new)
		output dictionary.
	@rtype: dict
	"""
	o = d.copy()
	for t in l:
		if o.has_key(t):
			del o[t]
	return o



def rev1to1(d):
	"""Reverse a 1-1 mapping so it maps values to keys
	instead of keys to values.
	@type d: dict
	@rtype: dict
	@return: M such that if m[k]=v, M[v]=k
	"""
	o = {}
	for (k, v) in d.items():
		if v in o:
			raise ValueError, 'Dictionary is not 1 to 1 mapping'
		o[v] = k
	return o


def add_dol(dict, key, value):
	"""Add an entry to a dictionary of lists.
	A new list is created if necessary; else the value is
	appended to an existing list.
	Obsolete: replace with dict_of_lists.
	"""
	try:
		dict[key].append(value)
	except KeyError:
		dict[key] = [ value ]


def add_doc(dict, key, value):
	"""Add an entry to a dictionary of counters.
	A new counter is created if necessary; else the value is
	added to an existing counter.
	Obsolete: replace with dict_of_accums.
	"""
	try:
		dict[key] += value
	except KeyError:
		dict[key] = value


class dict_of_lists(dict):
	"""A dictionary of lists."""

	def add(self, key, value):
		"""Append value to the list indexed by key."""
		try:
			self[key].append(value)
		except KeyError:
			self[key] = [ value ]

	def addgroup(self, key, values):
		"""Append values to the list indexed by key."""
		try:
			self[key].extend(values)
		except KeyError:
			self[key] = values

	def add_ifdifferent(self, key, value):
		"""Append value to the list indexed by key."""
		try:
			v = self[key]
		except KeyError:
			self[key] = [value]
		else:
			if value not in v:
				v.append( value )

	def copy(self):
		"""This does a shallow copy."""
		return dict_of_lists(self)


	def merge(self, other):
		for (k, v) in other:
			self.addgroup(k, v)


class dict_of_sets(dict):
	"""A dictionary of lists."""
	def add(self, key, value):
		"""Append value to the set indexed by key."""
		try:
			self[key].add(value)
		except KeyError:
			self[key] = set([value])

	def addgroup(self, key, values):
		"""Append values to the list indexed by key."""
		try:
			self[key].update(values)
		except KeyError:
			self[key] = set(values)


	def copy(self):
		"""This does a shallow copy."""
		return dict_of_sets(self)


	def merge(self, other):
		for (k, v) in other:
			self.addgroup(k, v)


class dict_of_accums(dict):
	"""A dictionary of accumulators.
	Note that the copy() function produces a dict_of_accums."""

	def add(self, key, value):
		"""Add value to the value indexed by key."""
		try:
			self[key] += value
		except KeyError:
			self[key] = value


	def copy(self):
		return dict_of_accums(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)


class dict_of_averages(dict):
	"""A dictionary of accumulators.
	Note that the copy() function produces a dict_of_averages."""

	def add(self, key, value, weight=1.0):
		"""Add value to the value indexed by key."""
		assert weight >= 0.0
		if key in self:
			self[key] += complex(value*weight, weight)
		else:
			self[key] = complex(value*weight, weight)

	def get_avg(self, key):
		vw = self[key]
		assert vw.imag > 0.0, "Weight for key=%s is nonpositive(%g)" % (k, vw.imag)
		return vw.real/vw.imag

	def get_avgs(self):
		o = {}
		for (k, vw) in self.items():
			assert vw.imag > 0.0, "Weight for key=%s is nonpositive(%g)" % (k, vw.imag)
			o[k] = vw.real/vw.imag
		return o


	def copy(self):
		return dict_of_averages(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)


class dict_of_maxes(dict):
	"""A dictionary of maxima.   Add a new number and the stored
	maximum will increase iff the new value is bigger.
	Note that the copy() function produces a dict_of_accums."""

	def add(self, key, value):
		"""Add value to the value indexed by key."""
		try:
			tmp = self[key]
			if value > tmp:
				self[key] = value
		except KeyError:
			self[key] = value


	def copy(self):
		return dict_of_maxes(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)



class dict_of_X(dict):
	"""A dictionary of arbitrary things.
	Note that the copy() function produces a dict_of_X.
	"""

	def __init__(self, constructor, incrementer):
		self.constructor = constructor
		self.incrementer = incrementer

	def add(self, key, *value):
		"""Add value to the thing indexed by key."""
		try:
			self.incrementer(self[key], *value)
		except KeyError:
			self[key] = self.constructor(*value)


class list_of_dicts(list):
	def __init__(self, *arg):
		list.__init__(self, arg)
	
	def lookup1(self, key, value):
		for d in self:
			try:
				if d[key]==value:
					return d
			except KeyError:
				pass
