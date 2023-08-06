import types

class proxy_object(object):
	pass


def transform_callable(onm, obj):
	print 'Making', onm, 'with', obj
	def tmp(self, *a, **kw):
		print '#', onm, obj, obj.__doc__, '(',id(self), a, kw, ')'
		o = object.__getattribute__(self, 'o')
		return obj(o, *a, **kw)
	return tmp


def create_property(onm):
	def fget(self):
		o = object.__getattribute__(self, 'o')
		return getattr(o, onm)
	def fset(self, v):
		o = object.__getattribute__(self, 'o')
		return setattr(o, onm, v)
	def fdel(self):
		o = object.__getattribute__(self, 'o')
		return delattr(o, onm)
	return property(fget, fset, fdel)


def proxyclass(oc):
	nm = 'Proxy_to_' + oc.__name__
	b = [ cached_proxyclass(bs) for bs in oc.__bases__ ]
	print 'b=', b
	d = {}

	print 'oc.__dict__=', oc.__dict__.keys()
	for (onm, obj) in oc.__dict__.items():
		if onm in ['__dict__', '__class__', '__weakref__', '__init__',
				'__getattribute__', '__setattr__', '__delattr__',
				'__del__', '__new__']:
			pass
		# elif type(obj) == types.FunctionType:
		elif callable(obj):
			d[onm] = transform_callable(onm, obj)
		else:
			d[onm] = create_property(onm)

	def __init__(self, o):
		"""proxyclass.__init__"""
		print 'Proxy __init__', o
		object.__setattr__(self, 'o', o)

	def __setattr__(self, k, v):
		print '--setattr--'
		o = object.__getattribute__(self, 'o')
		setattr(o, k, v)

	def __delattr__(self, k):
		o = object.__getattribute__(self, 'o')
		delattr(o, k)

	def __getattribute__(self, k):
		if k in ('__class__',):
			print '[-get-', k, ']'
			return object.__getattribute__(self, k)
		o = object.__getattribute__(self, 'o')
		tmp = getattr(o, k)
		print '[__getattribute__(', self, k, ')=', tmp
		return tmp

	def __del__(self):
		object.__delattr__(self, 'o')



	d['__init__'] = __init__
	d['__setattr__'] = __setattr__
	d['__delattr__'] = __delattr__
	d['__getattribute__'] = __getattribute__
	d['__del__'] = __del__
	print 'd=', d
	return type(nm, tuple(b), d)


classcache = {id(object): proxy_object, id(type): proxy_object,
		id(proxy_object): proxy_object
		}
def cached_proxyclass(oc):
	global classcache
	try:
		return classcache[id(oc)]
	except KeyError:
		tmp = proxyclass(oc)
		classcache[id(oc)] = tmp
	return tmp


def proxymaker(o):
	return cached_proxyclass(o.__class__)(o)


class foo(object):
	def __init__(self):
		"""foo.__init__"""
		self.x = 1

	def __getitem__(self, k):
		return self.x + k

x = foo()
# y = generic_proxy(x)
# print type(x)
# print type(y)
# print y.__class__
# print x[4]
# print y[4]
# print '---'
z = proxymaker(x)
print 'ZCD', z.__class__.__dict__
print 'XCD', x.__class__.__dict__
print 'z.x=', z.x
z.x = 2
assert x.x == 2
assert z.x == 2
x.x = 3
assert z.x == 3
assert x.x == 3
print 'z[4]=', z[int(4)]
assert x[6] == 9
assert z[6] == 9
assert x[4] == z[4]
print 'dir(x)=', dir(x)
print 'dir(z)=', dir(z)
print z.__class__
assert isinstance(z, cached_proxyclass(foo))
assert isinstance(z, proxy_object)
assert isinstance(z, object)
print '------'

class foofoo(foo):
	def __init__(self):
		"""foofoo.__init__"""
		foo.__init__(self)
		self.xx = 12

	def __str__(self):
		return '<A FOOFOO>'
	
	def __repr__(self):
		return '<REPR FOOFOO>'
	
	def tmp(self):
		return 'q'
	
	def __getitem__(self, k):
		return foo.__getitem__(self, k)+1

xx = foofoo()
zz = proxymaker(xx)
print 'zz.x', zz.x, zz.xx
print 'zz[10]=', zz[10]
print 'zz=', str(zz), repr(zz), zz
assert isinstance(zz, cached_proxyclass(foofoo))
assert isinstance(xx, foofoo)
assert isinstance(zz, cached_proxyclass(foo))
assert isinstance(xx, foo)
assert isinstance(zz, proxy_object)
assert isinstance(zz, object)
assert isinstance(xx, object)

print '============'

import sys
zz = proxymaker(sys)
print 'sys.path', sys.path
print dir(zz)

print '++++++++'

zz = proxymaker(3)
print zz, zz+1
zz = proxymaker(3.0)
print zz, zz+1.0

print 'ooooooooooooo'

fd = open('/dev/null', 'r')
zz = proxymaker(fd)
assert fd.closed == zz.closed
print 'readline=', zz.readline()
print type(zz)
print dir(zz)
