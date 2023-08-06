"""This module has functions that help you dynamically import modules.
"""



import sys
import imp
import os.path

def split_name(name):
	"""Split a name in the form    a/b.c into a, b, c, where
	a is a search path,
	b is a module (package) name, and
	c is a name in the module.
	"""
	p = None
	fcn = []
	if '/' in name:
		p, name = os.path.split(name)
	if '.' in name:
		a = name.split('.')
		name = a[0]
		fcn = a[1:]
	return (p, name, fcn)


def load(name, path):
	"""Load a module from the specified path, or, failing that,
	look in sys.path then for a builtin.   It returns the module,
	but does not import it.
	If path is None, only look in sys.path and builtins.
	If path is an array containing None, replace the None with sys.path.

	This version gives you detailed control over the search path.
	"""
	if path is None:
		pth = None
	else:
		pth = []
		for d in path:
			if d is None:
				pth.extend(sys.path)
			else:
				pth.append( d )
	fd = None
	imp.acquire_lock()
	try:
		fd, pn, desc = imp.find_module(name, pth)
	except ImportError:
		try:
			fd, pn, desc = imp.find_module(name, None)
		except:
			imp.release_lock()
			raise

	if name in sys.modules:
		if hasattr(sys.modules[name], '__file__'):
			if os.path.dirname(sys.modules[name].__file__) == os.path.dirname(pn):
				imp.release_lock()
				return sys.modules[name]
		else:
			imp.release_lock()
			return sys.modules[name]

	try:
		pymod = imp.load_module(name, fd, pn, desc)
	finally:
		if fd:
			fd.close()
		imp.release_lock()
	return pymod


load_mod = load
load_inc_path = load
load_mod_inc_path = load_inc_path

def load_named(name, use_sys_path=True):
	"""Load a module.
	If the module name is in the form a/b,
	it looks in directory "a" first.
	If use_sys_path is true, it searches the entire Python path
	
	It returns the module, but does not import it.
	This version handles importing packages and functions nicely,
	but with less control over the search path.
	
	Usage:
		- load_named_module('/dir/my_module'), or
		- load_named_module('foo/my_module'), or
		- load_named_module('foo/my_module.submodule.function'), or
		- various combinations.
	"""
	p, name, attrlist = split_name(name)
	if use_sys_path:
		path = sys.path[:]
	else:
		path = []
	if p is not None:
		path.insert(0, p)
	try:
		tmp = load(name, path)
	except ImportError, x:
		raise ImportError, "%s in '%s'%s" % (str(x), p, ['', ' or sys.path'][use_sys_path])

	filename = getattr(tmp, '__file__', None)
	if filename is None:
		filename = getattr(tmp, '__name__', '???')
	try:
		for (i,a) in enumerate(attrlist):
			tmp = getattr(tmp, a)
	except AttributeError:
		raise ImportError, "Lookup fails after import on %s/%s while attempting %s" % (
					filename, '.'.join(attrlist[:i+1]), name
					)
	return tmp


load_named_module = load_named
load_named_fcn = load_named
load_fcn = load_named

def _test():
	assert abs(load_named('math.pi') - 3.14159) < 0.001
	assert load_named('load_mod.load_named.__doc__') == load_named.__doc__
	f = os.path.splitext(__file__)[0]
	assert load_named('%s.load' % f).__doc__ == load.__doc__

if __name__ == '__main__':
	_test()
