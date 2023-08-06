from bitmat import BitMat, NodeKeyDict, SUBJECT, PREDICATE, OBJECT
from tests.data import *
from sys import stdout
import logging 

log = logging.getLogger("fold")

graph = eswc.memory()
nodes = NodeKeyDict()

class TestClass:
	def test_fold(self):
		"""
		Check fold/unfold
		"""
		def test(retain):
			stdout.write("retain %s... " % (retain,))
			stdout.flush()
			bitmat = BitMat(graph, nodes)
			result, mask = bitmat.fold(retain, (None, None, None))
			result = bitmat.unfold(result, mask)
			r1 = list(graph.triples((None, None, None)))
			r2 = list(result)
			r1.sort()
			r2.sort()
			assert r1 == r2
		for retain in SUBJECT, PREDICATE, OBJECT:
			yield test, retain
