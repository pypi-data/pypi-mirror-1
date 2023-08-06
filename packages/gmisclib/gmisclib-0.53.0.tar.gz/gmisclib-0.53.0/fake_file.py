"""A class that implements a simple file in memory.
It's not an exact simulation of a real file:
it assumes that no seeking is done, and that
all reads are line-at-a-time.
It also (intentionally) allow reading from files opend
in mode 'r', and allows writing for files opened in mode
'w'."""

import types

__version__ = "$Revision: 1.4 $"


class file:
	def __init__(self, name, mode):
		assert mode in ['r', 'w',  'rw',  'wr'], "Bad mode: %s" % mode
		self.name = name
		self.mode = mode
		self.buf = ['']
		self.p = 0

	def write(self, data):
		if len(data) == 0:
			return 0
		self.buf[-1] = self.buf[-1] + data
		if data[-1] == '\n':
			self.buf.append('')
		return len(data)

	def writelines(self, a):
		if type(a) == types.StringType:
			self.write(a)
			return
		for t in a:
			self.write(t)

	def readline(self):
		if self.p >= len(self.buf):
			return ''
		tmp = self.buf[self.p]
		self.p += 1
		return tmp


	def readlines(self):
		if self.p >= len(self.buf):
			return []
		tmp = self.buf[self.p:]
		if tmp[-1] == '':
			tmp = tmp[:-1]
			self.p = len(self.buf) - 1
		else:
			self.p = len(self.buf)
		return tmp


	def flush(self):
		pass


	def close(self):
		pass



def open(name, mode):
	return file(name, mode)



if __name__ == '__main__':
	x = file("foo", "rw")
	x.write("Hello\n")
	x.write("foo\n")
	assert x.readline() == "Hello\n"
	assert x.readline() == "foo\n"
	assert x.readline() == ''
	assert x.readlines() == []

	x = file("foo", "rw")
	x.write("Hello\n")
	x.write("foo\n")
	assert x.readlines() == [ 'Hello\n', 'foo\n' ]
