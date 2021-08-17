# authored by Benjamin Gerard and Aditya Sengupta (and Sylvain Cetre?)

from abc import ABC, abstractmethod
import numpy as np
from copy import copy
import warnings

from ..utils import joindata

class Optics(ABC): 
	@property
	def dmzero(self):
		return np.zeros(self.dmdims, dtype=np.float32)

	def applyzero(self):
		self.applydmc(self.dmzero, False)

	def refresh(self, verbose=True):
		bestflat = np.load(joindata("bestflats/bestflat.npy"))
		dmc = self.getdmc()
		self.applydmc(bestflat)
		imflat = self.stack(100)
		np.save(joindata("bestflats/imflat.npy"), imflat)
		if verbose:
			print("Updated the flat image.")
		self.applydmc(dmc)
		return bestflat, imflat

	def stack(self, n):
		ims = self.getim()
		for _ in range(n-1):
			ims = ims + self.getim()
		ims = ims/n
		return ims

	@abstractmethod
	def getim(self):
		pass

	@abstractmethod
	def getdmc(self):
		pass

	@abstractmethod
	def applydmc(self, cmd):
		pass

	@abstractmethod
	def set_expt(self, t):
		pass

	@abstractmethod
	def get_expt(self):
		pass

class FAST(Optics):
	def __init__(self):
		self.a = shmlib.shm('/tmp/ca03dit.im.shm') 
		self.im = shmlib.shm('/tmp/ca03im.im.shm')
		self.b = shmlib.shm('/tmp/dm02itfStatus.im.shm')
		status = b.get_data()
		status[0,0] = 1
		self.b.set_data(status)
		self.dmChannel = shmlib.shm('/tmp/dm02disp01.im.shm')
		self.dmdims = getdmc().shape

	def set_expt(self, t):
		'''
		change the exposure time

		for the large array the smallest exposure time is around 1e-5
		'''
		dit = self.a.get_data()
		dit[0][0] = t; self.a.set_data(dit)
	
	def get_expt(self):
		return self.a.get_data()[0][0]

	def getim(self):
		return self.im.get_data(check=True)

	def getdmc(self): # read current command applied to the DM
		return self.dmChannel.get_data()

	def applydmc(self, dmc): #apply command to the DM
		"""
		Applies the DM command `dmc`.
		Returns two booleans: whether the command is in range below (everything is >=0), and above (everything is <=1),
		unless verbose=False, in which case nothing is returned.
		"""
		if np.any(dmc < 0):
			warnings.warn("saturating DM zeros!")
		if np.any(dmc > 1):
			warnings.warn("saturating DM ones!")
		dmc = np.maximum(0, np.minimum(1, dmc))
		self.dmChannel.set_data(dmc)

class Sim(Optics):
	def __init__(self):
		from ..constants import dmdims, imdims
		self.dmdims = dmdims
		self.imdims = imdims
		self.t = 1e-3
		self.dmc = copy(self.dmzero)

	def expt(self, t):
		warnings.warn("Exposure time in sim optics is not used yet.")
		self.t = t

	def get_expt(self):
		warnings.warn("Exposure time in sim optics is not used yet.")
		return self.t

	def getim(self):
		warnings.warn("Image propagation from the DM has not been implemented.")
		return np.zeros(self.imdims, dtype=np.float32)

	def getdmc(self):
		return self.dmc

	def applydmc(self, dmc):
		self.dmc = np.maximum(0, np.minimum(1, dmc))
	
	
try:
	from krtc import shmlib
	optics = FAST()
except (ModuleNotFoundError, OSError):
	print("Running in simulation mode.")
	optics = Sim()
