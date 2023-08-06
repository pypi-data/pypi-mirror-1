from rdflib.store.Sleepycat import Sleepycat
from rdflib.graph import Graph
from os import stat
import logging
import swiss
import gzip

__all__ = ["tbl", "eswc", "uniprot"]

CACHE_DIR="data"
cache = swiss.Cache(CACHE_DIR)

class Cached(object):
	def __init__(self):
		self.log = logging.getLogger(self.__class__.__name__)
	def file(self):
		fname = cache.retrieve(self.url)
		return fname
	def memory(self):
		g = Graph()
		g.parse(self.file())
		return g
	def sleepy(self):
		db = CACHE_DIR + "/" + self.__class__.__name__ + ".sleepy"
		try:
			stat(db)
			create = True
		except OSError:
			create = True
		store = Sleepycat(db)
		g = Graph(store)
		if create:
			self.log.info("parsing graph")
			g.parse(self.file())
			g.commit()
			self.log.info("done")
		return g

class TBL(Cached):
	url = "http://www.w3.org/People/Berners-Lee/card"
tbl = TBL()

class ESWC(Cached):
	url = "http://data.semanticweb.org/dumps/conferences/eswc-2007-complete.rdf"
eswc = ESWC()

class UNIPROT(Cached):
	## 7Gb file
	#url = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprot.rdf.gz"
	## 350Mb file
	#url = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/citations.rdf.gz"
	## 12Mb file
	#url = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/taxonomy.rdf.gz"
	url = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/enzyme.rdf.gz"
	def file(self):
		fname = super(UNIPROT, self).file()
		return gzip.open(fname)
uniprot = UNIPROT()

if __name__ == '__main__':
	from datetime import datetime
	start = datetime.now()
	print "Starting... %s" % (start,)
	g = uniprot.sleepy()
	end = datetime.now()
	print "Parsed in %s" % (end-start,)
	print len(g)
