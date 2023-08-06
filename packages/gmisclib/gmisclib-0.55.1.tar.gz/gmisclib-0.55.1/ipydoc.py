#!/usr/bin/env python

import pydoc
import q3html
from q3html import needcopy, swapend
import re
import os
import die
die.debug = 0

_ck_py = re.compile('for|import|def|None')
_name_py = re.compile('.*[.]py$')
_ck_html = re.compile('< *(TITLE|title)|href|img|< *[pP]|< *[aA]')
_name_html = re.compile('.*[.]html$')

def _checkfile(f, repat):
	fd = open(f, "r")
	for l in fd:
		if repat.match(l):
			return 1
	return 0


def _findfiles(dir, namepat, repat):
	die.note("directory", dir)
	die.note("File name regexp", namepat.pattern)
	die.note("File contents regexp", repat.pattern)
	o = []
	l = os.listdir(dir)
	# print "L=", l
	for t in l:
		ts = t.strip()
		x = namepat.match(ts)
		# print "ts=", ts, "match=", x
		if not x:
			continue
		if not _checkfile(ts, repat):
			die.info("File %s doesn't seem to have the correct contents. Ignored." % ts)
			continue
		o.append(ts)
	return o


def find_py(dir):
	return _findfiles(dir, _name_py, _ck_py)


def find_html(dir):
	return _findfiles(dir, _name_html, _ck_html)


if __name__ == '__main__':
	import sys
	sys.path.insert(0, '.')
	target = sys.argv[1]
	if not os.path.isdir(target):
		die.info("Making directory %s" % target)
		os.makedirs(target)
	for n in find_py('.'):
		nh = swapend(n, '.html')
		if not needcopy(n, nh):
			die.dbg("No need to process %s" % n)
			continue
		pydoc.writedoc(swapend(n, ''))
	upload = q3html.easygo()
	htmllist = find_html('.')
	for n in htmllist:
		nt = '%s/%s' % (target, n)
		if not needcopy(n, nt):
			die.dbg("No need to copy %s" % n)
			continue
		die.info("Copying %s -> %s" % (n, nt))
		tmp = os.system("cp %s %s" %( n, nt))
		assert tmp==0
