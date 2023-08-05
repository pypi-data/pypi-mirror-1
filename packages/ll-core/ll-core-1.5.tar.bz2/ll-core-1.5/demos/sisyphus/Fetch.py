#!/usr/local/bin/python

import os
import urllib
from ll import sisyphus

class Fetch(sisyphus.Job):
	"""
	fetches an HTML from an URL and (savely) copies it to a target file.
	"""
	def __init__(self):
		sisyphus.Job.__init__(self, 180, name="Fetch")
		self.url = "http://www.python.org/"
		self.tmpname ="Fetch_Tmp_"  + str(os.getpid()) + ".html"
		self.officialname = "Python.html"

	def execute(self):
		self.logProgress("fetching data from %r" % self.url)
		data = urllib.urlopen(self.url).read()
		datasize = len(data)
		self.logProgress("writing file %r (%d bytes)" % (self.tmpname, datasize))
		open(self.tmpname, "wb").write(data)
		self.logProgress("renaming file %r to %r" % (self.tmpname, self.officialname))
		os.rename(self.tmpname, self.officialname)
		self.logLoop("cached %r as %r (%d bytes)" % (self.url, self.officialname, datasize))

if __name__=="__main__":
	sisyphus.execute(Fetch())
