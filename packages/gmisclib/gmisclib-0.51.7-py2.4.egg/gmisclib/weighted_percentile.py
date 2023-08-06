import Num


def wp(data, wt, percentiles):
	assert Num.alltrue(Num.greater_equal(percentiles, 0.0)), "Percentiles less than zero"
	assert Num.alltrue(Num.less_equal(percentiles, 1.0)), "Percentiles greater than one"
	data = Num.asarray(data)
	if wt is None:
		wt = Num.ones(data.shape, Num.Float)
	else:
		wt = Num.asarray(wt, Num.Float)
		assert wt.shape == data.shape
		assert Num.alltrue(Num.greater_equal(wt, 0.0)), "Not all weights are non-negative."
	assert len(wt.shape) == 1
	assert len(data.shape) == 1
	n = data.shape[0]
	i = Num.argsort(data)
	sd = Num.take(data, i, axis=0)
	sw = Num.take(wt, i, axis=0)
	aw = Num.add.accumulate(sw)
	if not aw[-1] > 0:
		raise ValueError, "Nonpositive weight sum"
	w = (aw-0.5*sw)/aw[-1]
	spots = Num.searchsorted(w, percentiles)
	o = []
	for (s, p) in zip(spots, percentiles):
		if s == 0:
			o.append(sd[0])
		elif s == n:
			o.append(sd[n-1])
		else:
			f1 = (w[s] - p)/(w[s] - w[s-1])
			f2 = (p - w[s-1])/(w[s] - w[s-1])
			assert f1>=0 and f2>=0 and f1<=1 and f2<=1
			assert abs(f1+f2-1.0) < 1e-6
			o.append(sd[s-1]*f1 + sd[s]*f2)
	return o



def test():
	assert Num.allclose(wp([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], None,
					[0.0, 1.0, 0.5, 0.51, 0.49, 0.01, 0.99]),
				[1.0, 10.0, 5.5, 5.6, 5.4, 1.0, 10.0], 0.0001)
	assert Num.allclose(wp([0, 1, 2, 3, 4], [0.1, 1.9, 1.9, 0.1, 1],
					[0.0, 1.0, 0.01, 0.02, 0.99]),
					[0.0, 4.0, 0.0, 0.05, 4.0], 0.0001)



if __name__ == '__main__':
	test()
