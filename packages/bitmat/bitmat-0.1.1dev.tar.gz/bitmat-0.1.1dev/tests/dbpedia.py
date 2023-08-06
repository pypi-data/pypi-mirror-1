from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib.store.Sleepycat import Sleepycat
from datetime import datetime
from bitmat import BitMat
from bz2 import BZ2File
from os import makedirs, stat
import swiss 

cache = swiss.Cache("data")
uri = "http://downloads.dbpedia.org/3.4/en/infobox_en.nt.bz2"

if __name__ == '__main__':
	parse = True

        store = Sleepycat("dbpedia.bdb")
        g = Graph(store)

        if parse:
		start = datetime.now()
		fname = cache.retrieve(uri)
		g.parse(BZ2File(fname), format="n3")
		end = datetime.now()
		print "Read %d triples in %s" % (len(g), end-start)

	m = BitMat()
	start = datetime.now()
	m.parse(g.triples((None, None, None)))
	end = datetime.now()
	print "Made BitMat in %s" % (end-start,)

