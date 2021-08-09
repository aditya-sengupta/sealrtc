# authored by Benjamin Gerard (and Sylvain Cetre?)

from krtc import shmlib
import pysao
import numpy as np
import warnings

try:
    ds9 = pysao.ds9()
except OSError:
    pass

#initialize; no need to load this more than once
#for full frame:

a = shmlib.shm('/tmp/ca03dit.im.shm') 
im = shmlib.shm('/tmp/ca03im.im.shm')

#for 150x150 subarray
'''
a = shmlib.shm('/tmp/ca03dit.im.shm') 
im = shmlib.shm('/tmp/ca03im.im.shm')
'''
def expt(t):
	'''
	change the exposure time

	for the large array the smallest exposure time is around 1e-5
	'''
	dit = a.get_data()
	dit[0][0] = t; a.set_data(dit)

def get_expt():
	return a.get_data()[0][0]

def set_expt(t):
	expt(t)

#To view images in pysao ds9:
def getim():
	return im.get_data(check=True)

def vim(): #view image
	ds9.view(getim())

def vmtf(): #view image MTF
	imm = getim()
	mtf = np.abs(np.fft.fftshift(np.fft.fft2(imm)))
	ds9.view(mtf)

def stack(n):
	ims = getim()
	for _ in range(n-1):
		ims = ims+getim()
	ims = ims/n
	return ims

def cm(im):
	r, c = im.shape
	xv, yv = np.sum(im, axis=0), np.sum(im, axis=1)
	return (xv @ np.arange(r)) / np.sum(im), (yv @ np.arange(r)) / np.sum(im)

mtf = lambda im: np.abs(np.fft.fftshift(np.fft.fft2(im)))

#kilo DM commands

b = shmlib.shm('/tmp/dm02itfStatus.im.shm')
status = b.get_data()
status[0,0] = 1
b.set_data(status)
dmChannel = shmlib.shm('/tmp/dm02disp01.im.shm')

def getdmc(): # read current command applied to the DM
	return dmChannel.get_data()

def applydmc(cmd, verbose=True): #apply command to the DM
	"""
	Applies the DM command `cmd`.
	Returns two booleans: whether the command is in range below (everything is >=0), and above (everything is <=1),
	unless verbose=False, in which case nothing is returned.
	"""
	indneg = np.where(cmd<0)
	if len(indneg[0])>0:
		cmd[indneg] = 0 #minimum value is zero
		warnings.warn('saturating DM zeros!')
	indpos = np.where(cmd>1)
	if len(indpos[0])>0:
		cmd[indpos] = 1 #maximum value is 1
		warnings.warn('saturating DM ones!')
	dmChannel.set_data(cmd)
	if verbose:
		return (len(indneg[0]) <= 0, len(indpos[0]) <= 0)

dmcini = getdmc()
dmzero = np.zeros(dmcini.shape, dtype=np.float32)
applyzero  =  lambda : applydmc(dmzero, False)