"""This takes anticorrelated samples from a sequence of data.
In other words, it tends to choose data that have not been seen
frequently before.   With blueness=1, it never shows a sample
n times until all samples have been shown n-1 times.

(Note that it is possible for an item to appear twice in sucession,
if it appears as the Nth item in a set of N, then appears as the first
item in the second set of N.)
"""

import heapq
import random
import math



class bluedata:
	def __init__(self, data, blueness=2.0):
		assert blueness > 0.0
		self.blue = float(blueness)
		self.q = [ (random.random(), datum) for datum in data ]
		heapq.heapify(self.q)


	def add(self, datum):
		heapq.heappush(self.q, (random.random(), datum) )


	def pickiter(self, n):
		"""Pick n items from the data set."""
		for i in range(n):
			u, d = heapq.heappop(self.q)
			heapq.heappush( self.q, (math.floor(u) + self.blue + random.random(), d) )
			yield d

	def pick(self, n):
		"""Pick n items from the data set."""
		return list(self.pickiter(n))

	def split(self, n):
		"""Split the data set into two parts, of size  n and len(data)-n.
		Successive calls to split will avoid having the same items appear
		in the first part.   For instance, given a bluedata of size 100,
		with ten calls to split(10), each datum will appear in the first
		part of the return tuple exactly once.
		"""
		assert n <= len(self.q), "Split requires 0 <= n <= len."
		o1 = []
		o2 = []
		nq = []
		while len(o1) < n:
			u, d = heapq.heappop(self.q)
			o1.append( d )
			heapq.heappush(nq, (int(u) + self.blue + random.random(), d) )
		for (u, d) in self.q:
			o2.append(d)
			heapq.heappush(nq, (int(u) + random.random(), d) )
		self.q = nq
		return (o1, o2)


	def __iter__(self):
		"""This iterator will produce samples forever."""
		while True:
			u, d = heapq.heappop(self.q)
			heapq.heappush(self.q, (int(u) + self.blue + random.random(), d) )
			yield d


	def __len__(self):
		return len(self.q)


	def reset(self):
		"""Forget prior history of usage.   Choices after this
		call are uncorrelated with choices before this call."""
		self.q = [ (random.random(), d) for (u, d) in self.q ]



def test():
	data = [0, 1, 2, 3, 4, 5, 6]
	x = bluedata(data)
	data.sort()
	o1 = x.pick(3) 
	o2 = x.pick(4)
	o = o1 + o2
	o.sort()
	assert o == data
	o1 = x.pick(2)
	o2 = x.pick(5)
	o = o1 + o2
	o.sort()
	assert o == data
	o1 = x.pick(1)
	o2 = x.pick(6)
	o = o1 + o2
	o.sort()
	assert o == data
	o1 = x.pick(7)
	o2 = x.pick(0)
	o = o1 + o2
	o.sort()
	assert o == data
	o = x.pick(len(data))
	o.sort()
	assert o == data

	assert len(x) == len(data)

	tmp = []
	for (i, q) in enumerate(x):
		tmp.append(q)
		if len(tmp) >= len(data):
			break
	tmp.sort()
	assert tmp == data

if __name__ == '__main__':
	test()
