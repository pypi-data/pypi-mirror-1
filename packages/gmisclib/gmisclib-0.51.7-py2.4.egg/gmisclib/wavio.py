#!/usr/bin/env python

"""When run as a script:
python ~/lib/wavio.py [-g gain] -wavin|-wavout infile outfile
Reads or writes .wav files from any format supported by
gpkimgclass.py .

As a library, allows reading of class gpk_img data from a .WAV
file, and writing class gpk_img to a .WAV file.
"""
import Num
import wave
import gpkimgclass

#: Cause L{write} to raise an error on overflow.
OV_ERROR = 0
#: Cause L{write} to truncate overflows.
OV_LIMIT = 1
#: Cause L{write} to silently ignore overflows.
OV_IGNORE = 2

_sizes = {
	2: (Num.int16, 16),
	4: (Num.int32, 32)
	}

def read(fn):
	"""Reads in a .WAV file and returns a L{gpkimgclass.gpk_img} instance
	that contains the header and data information.
	@param fn: filename
	@type fn: str
	@return: audio data
	"""

	w = wave.open(fn, "r")
	assert w.getcomptype() == 'NONE', "Can't handle %s compression" % w.getcompname()
	nf = w.getnframes()
	nc = w.getnchannels()
	dt = 1.0/w.getframerate()
	numtype, bitpix = _sizes[w.getsampwidth()]
	data = Num.fromstring(w.readframes(nf), numtype)
	w.close()
	data = Num.reshape(data, (nf, nc))
	hdr = {
		'NAXIS1': nc, 'NAXIS2': nf,
		'CDELT2': dt, 'CRPIX2': 1, 'CRVAL2': 0.0,
		'BITPIX': bitpix
		}
	return gpkimgclass.gpk_img(hdr, data)


def _itemsize(z):
	"""This exists for Numeric/NumPy compatibility"""
	x = z.itemsize
	if isinstance(x, int):
		return x
	if callable(x):
		return x()
	raise RuntimeError, 'Cannot deal with %s' % str(type(x))

_typecodes = {
	_itemsize(Num.zeros((1,), Num.Int32))*8:
			(Num.Int32, 2.0**31-1.0, 1.0-2.0**31),
	_itemsize(Num.zeros((1,), Num.Int16))*8:
			(Num.Int16, 2.0**15-1.0, 1.0-2.0**15),
	_itemsize(Num.zeros((1,), Num.Int8))*8:
			(Num.Int8, 2.0**7-1.0, 1.0-2.0**7)
	}

def write(data, fname, scalefac=1, allow_overflow=OV_ERROR):
	"""@param data: is a class gpk_img object containing
		data to be written (note that the header information is
		ignored except for the sampling rate, bits per pixel,
		and number of channels.
	@param fname: is the name of a file to write it to,
	@param scalefac: is a factor to multiply the data
	@param allow_overflow: can be either
		- L{OV_ERROR} (default, means raise a ValueError exception
			if the data*scalefac overflows),
		- L{OV_LIMIT} (means limit the data*scalefac to prevent
			overflows -- this clips the audio), or
		- L{OV_IGNORE} (means let the overflows happen and don't worry.)
	"""
	if not (data.dt() > 0.0):
		raise ValueError, "Cannot set sampling rate: dt=%g\n" % data.dt()

	hdr = data.hdr

	if not hdr.has_key('BITPIX') or int(hdr['BITPIX'])==0:
		bitpix = 16
	else:
		bitpix = abs(int(hdr['BITPIX']))
	assert bitpix % 8 == 0
	if bitpix > 32:
		bitpix = 32

	tc, vmax, vmin = _typecodes[bitpix]
	dds = data.d * scalefac
	if allow_overflow == OV_ERROR:
		if not Num.alltrue(Num.greater_equal(Num.ravel(dds), vmin)):
			raise ValueError, "Scaled data overflows negative"
		if not Num.alltrue(Num.less_equal(Num.ravel(dds), vmax)):
			raise ValueError, "Scaled data overflows positive"
	elif allow_overflow == OV_LIMIT:
		dds = Num.clip(dds, vmin, vmax)
	else:
		assert allow_overflow == OV_IGNORE

	d = Num.around(dds).astype(tc).tostring()
	w = wave.open(fname, "w")
	w.setnchannels(data.d.shape[1])
	w.setnframes(data.d.shape[0])
	w.setsampwidth(bitpix/8)
	w.setframerate( int(round( 1.0/float(data.dt()) )) )
	w.writeframesraw(d)


if __name__ == '__main__':
	import sys
	import math
	arglist = sys.argv[1:]
	gain = None
	if len(arglist)==0:
		print __doc__
		sys.exit(1)
	if arglist[0] == '-g':
		arglist.pop(0)
		gain = float(arglist.pop(0))
	if arglist[0] == '-wavin':
		x = read(arglist[1])
		if gain is not None:
			Num.multiply(x.d, gain, x.d)
		x.write(arglist[2])
	elif arglist[0] == '-wavout':
		x = gpkimgclass.read(arglist[1])
		rxd = Num.ravel(x.d)
		mxv = max( rxd[Num.argmax(rxd)], -rxd[Num.argmin(rxd)] )
		print "# max=", mxv
		if gain is None:
			gain = 32000.0/mxv
		write(x, arglist[2], gain)
	else:
		print __doc__
		sys.exit(1)
