"""This module tells you if an object implements a class.
It lets you know if one class can substitute for another,
even if they are unrelated in an OO hierarchy.
For instance, if you need a write() method and
nothing else, this will check for it.
"""

import inspect
import sets

_cache = {}
MAXCACHE = 100

Optional = 'optional'
Varargs = 'varargs'
def Vartype(mem, com):
	return True
def Strict(mem, com):
	return False

Ignore = sets.Set( ['__class__', '__delattr__', '__module__', '__new__',
			'__doc__', '__dict__', '__getattribute__',
			'__hash__', '__repr__', '__str__',
			'__reduce__', '__reduce_ex__', '__setattr__',
			'__weakref__', '__slots__'
			]
		)


def why(instance, classobj):
	"""Explains why instance doesn't implement the classobj."""
	try:
		c = instance.__class__
	except AttributeError:
		return "Instance (arg 1) has no __class__ attribute."
	key = (c, classobj)
	try:
		return _cache[key]
	except KeyError:
		pass
	if len(_cache) > MAXCACHE:
		_cache.popitem()
	# for (mem, v) in inspect.getmembers(classobj):
	for mem in dir(classobj):
		if mem in Ignore:
			continue
		v = getattr(classobj, mem)
		gis = getattr(v, 'g_implements', Strict)
		if gis == Optional:
			continue
		if not hasattr(c, mem):
			_cache[key] = 'Missing member: %s; type=%s does not implement %s' % (mem, str(type(instance)), str(classobj))
			return _cache[key]
		com = getattr(c, mem)
		if callable(gis) and gis(mem, com):
			continue
		if inspect.ismethod(com):
			if inspect.ismethod(v):
				vargs, vv, vk, vdef = inspect.getargspec(v.im_func)
				margs, mv, mk, mdef = inspect.getargspec(com.im_func)
	
				if mdef is None:
					matchlen = len(margs)
				else:
					matchlen = len(margs)-len(mdef)
				if vargs[:matchlen] != margs[:matchlen]:
					if gis == Varargs:
						continue
					_cache[key] = "Method argument list does not match for %s: %s instead of %s; type=%s does not implement %s" \
								% (mem, margs[:matchlen], vargs[:matchlen],
									str(type(instance)), str(classobj))
					return _cache[key]
			elif inspect.ismethoddescriptor(v):
				continue
		elif type(com) != type(v):
			_cache[key] = 'Wrong type for %s: %s instead of %s; type=%s does not implement %s' \
					% (mem, type(com), type(v),
						str(type(instance)), str(classobj)
						)
			return _cache[key]
	_cache[key] = None
	return _cache[key]


def impl(instance, classobj):
	"""Tells you if an instance of an object implements a class.
	By implements, I mean that the instance supplies every member
	that the class supplies, and every member has the same type.
	The instance may have *more* members, of course.
	Functions require that the argument names must match, too
	at least as far as the required arguments in the classobj's function.

	The match may be made looser by adding a g_implements attribute
	to various class members.  Possibilities for the value
	are Optional, Strict, Vartype, Varargs, or you can give
	a two-argument function, and that function will be called
	to decide whether the match is acceptable or not.
	"""
	return why(instance, classobj) is None


def make_optional(x):
	"""This is a decorator for a function.
	make_optional implies make_varargs.
	"""
	x.g_implements = Optional
	return x

def make_varargs(x):
	"""This is a decorator for a function."""
	x.g_implements = Varargs
	return x

def make_vartype(x):
	"""This is a decorator for a function."""
	x.g_implements = Vartype
	return x

def make_strict(x):
	"""This is a decorator for a function."""
	x.g_implements = Strict
	return x


class GITypeError(TypeError):
	def __init__(self, s):
		TypeError.__init__(self, s)


def check(instance, classobj):
	w = why(instance, classobj)
	if w is not None:
		raise GITypeError, w


class _tc1(object):
	x = 1
	y = ''
	def z(self, foo):
		return foo

class _tc2(object):
	def __init__(self):
		pass

class _tc1a(object):
	x = 0
	y = 'x'
	def z(self, foo):
		return foo+1

class _tc3(object):
	x = 0.0
	y = 'x'
	def z(self, foo):
		return foo+1

class _tc1b(object):
	x = 0
	y = 'x'
	def z(self, foo):
		return foo+1
	w = []
	def foo(self, a, b):
		return a+b


class _tc0a(object):
	x = 1

class _tc0b(object):
	y = ''
	def z(self, foo):
		return 0

class _tc1c(_tc0a, _tc0b):
	pass

class _tc2a(object):
	x = 1
	y = ''
	def z(self, bar):
		return bar

def test():
	assert not impl(_tc1(), _tc2)
	check(_tc1(), _tc1a)
	assert not impl(_tc1(), _tc3)
	assert not impl(_tc1(), _tc1b)
	check(_tc1b(), _tc1)
	check(_tc1c(), _tc1)
	check(_tc1(), _tc1c)
	assert not impl(_tc1(), _tc2a)

if __name__ == '__main__':
	test()
