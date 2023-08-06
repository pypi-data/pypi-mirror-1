from bitmat import BitMat, NodeKeyDict, SUBJECT, PREDICATE, OBJECT
from bm import BitVector
from tests.utils import time
from tests.data import *
from sys import stdout
from rdflib.graph import Graph
from rdflib.namespace import RDF, RDFS, Namespace

import logging
log = logging.getLogger("join")

graph = eswc.memory()
nodes = NodeKeyDict()

DC = Namespace("http://purl.org/dc/elements/1.1/")
SWC = Namespace("http://data.semanticweb.org/ns/swc/ontology#")
SWRC = Namespace("http://swrc.ontoware.org/ontology#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

filters = [
	(SUBJECT, (None, SWRC["author"], None)),
	(SUBJECT, (None, RDFS.label, None)),
	(SUBJECT, (None, RDF.type, SWC["Paper"])),
	(SUBJECT, (None, DC["title"], None)),
]

class TestClass:
	def test_join(self):
		"""
		Time join
		"""
		binding = int(filters[0][0])
		@time
		def test():
			keydict = NodeKeyDict()
			bitmat = BitMat(graph, keydict)
			unique = BitVector()
			def _g():
				for binding, triple in bitmat.join(filters):
					binding = int(binding)
					key = keydict.get_key(triple[binding])
					if unique[key]:
						continue
					unique[key] = True
					yield triple[binding]
			## can't return a generator because then
			## the time function gives wrong results
			return list(_g())
		result = test()
		r1 = result
		### make the equivalent SPARQL query for comparison
		r2 = list(self.sparql_query())
		### SPARQL query doesn't do distinct properly for some reason...
		_r2 = {}
		for k in r2:
			_r2[k] = False
		r2 = _r2.keys()
		r1.sort()
		r2.sort()
		stdout.write("%d/%d (%d) results... " % (len(r1), len(r2), len(graph)))
		stdout.flush()
		assert r1 == r2

	def sparql_query(self):
		"""
		Kludgy function to create and execute a SPARQL
		query that should be equivalent to the joins done
		in test_join()
		"""
		from string import lowercase
		i = 0
		joins = []
		q = "SELECT DISTINCT ?join WHERE {\n"
		for j, (s, p, o) in filters:
			join = "\t"
			if j == SUBJECT:
				join = join + "?join "
			elif s:
				join = join + "<%s> " % (s,)
			else:
				join = join + "?%s" % (lowercase[i],)
				i = i + 1
			if j == PREDICATE:
				join = join + "?join "
			elif p:
				join = join + "<%s> " % (p,)
			else:
				join = join + "?%s " % (lowercase[i],)
				i = i + 1

			if j == OBJECT:
				join = join + "?join"
			elif o:
				join = join + "<%s>" % (o,)
			else:
				join = join + "?%s" % (lowercase[i],)
				i = i + 1
			joins.append(join)
		q = q + " .\n".join(joins) + "\n} GROUP BY ?join"
		log.debug(q)
		return graph.query(q, initNs = { "swc" : SWC, "swrc" : SWRC, "dc" : DC })

	def test_sparql(self):
		"""
		Time sparql
		"""
		test = time(self.sparql_query)
		test()
