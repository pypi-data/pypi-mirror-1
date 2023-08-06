

class thingie:
	i = 0

	def __init__(self):
		self.x = str(self.i)
		self.i += 1

def foo():
	tl = [ thingie() for k in range(100) ]
	return [ t for m in tl[-3:] ]


o = []
for i in range(1000):
	for j in range(1000):
		o.extend( foo() )
		print i
