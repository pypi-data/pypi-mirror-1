# $Id: FileHStore.py 52 2007-04-15 20:41:27Z adulau $

import hashlib
import sys
import os

class FileHStore:

	def __init__(self, path="", digest="sha256", level=1, debug="yes"):
		# hash store path
		self.path = path
		# digest to be use for the store
		self.digest = digest
		# number of subdirectories, default is 1 (deadbeef -> ./de/deadbeef)
		self.level = level
		# debug the operation on the store yes or no
		self.debug = debug

	def add(self, filepath):

		self._debug ("add" + filepath)
		id = self._doHash(filepath)
		fullpath = self._returnPath(id)
		fullpathfile = self._returnPath(id) + id
		
		if os.path.exists(fullpath):
			self._debug (fullpath + " already exists")
    		else:
        		os.makedirs(fullpath)

		if os.path.exists(fullpathfile):
		        self._debug (fullpathfile + " already exists")
		else:
			fr = open(filepath, "r")
			f = open(fullpathfile, "w")
			f.write(fr.read())
			f.close()
			fr.close()

		return id

	def getpath(self, id):

		self._debug("getpath " + id + " with digest " + self.digest)
		fullpath = self._returnPath(id)
		return fullpath+id

	def remove(self, id):

		self._debug("remove " + id + " with digest " + self.digest)

		fullpathfile = self._returnPath(id) + id

		if os.path.exists(fullpathfile):
		        self._debug (fullpathfile + " exists")
			os.unlink (fullpathfile)
		        self._debug (fullpathfile + " removed")
		else:
			self._debug (fullpathfile + " not existing...")
			return

	def _doHash(self, filename):

		f = open(filename, "r")
		h = hashlib.new(self.digest)
		h.update (f.read())
		f.close()
		return h.hexdigest()


	def _returnPath(self, id):

		fullpath = self.path + "/"

		for x in range(0, self.level*2, 2):
			fullpath = fullpath + id[x:2+x] + "/"

		return fullpath

	def _debug(self, message):

		if self.debug != 'no':
			print message

