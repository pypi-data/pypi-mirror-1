from rdflib.graph import Graph
from bm import BitVector

__all__ = ["BitMat", "BitMatError", "NodeKeyDict", "SUBJECT", "PREDICATE", "OBJECT"]

class _Node(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value
	def __str__(self):
		return self.name
	def __repr__(self):
		return repr(self.value)
	def __int__(self):
		return self.value
	def __eq__(self, other):
		return self.value == other
	

SUBJECT = _Node("subject", 0)
PREDICATE = _Node("predicate", 1)
OBJECT = _Node("object", 2)

class BitMatError(Exception):
	pass

class NodeKeyDict(object):
	def __init__(self):
		self.k2n = {}
		self.n2k = {}
		self._node_key = 0
	def __len__(self):
		return len(self.k2n)
	def next_key(self):
		i = self._node_key
		self._node_key = i + 1
		return i
	def get_key(self, node, default=None):
		if node is None:
			return default
		key = self.n2k.get(node, default)
		if key is default:
			key = self.next_key()
			self.n2k[node] = key
			self.k2n[key] = node
		return key
	def get_node(self, key, default=None):
		return self.k2n.get(key, default)

class BitMat(object):
	"""
	Given an RDF graph and a node/key dictionary, implement
	operations as described in

	http://tw.rpi.edu/wiki/BitMat:_A_Main_Memory_RDF_Triple_Store
	"""
	def __init__(self, graph, nodes):
		self.graph = graph
		self.nodes = nodes

	def fold(self, retain, (s,p,o), *av, **kw):
		"""
		Perform the fold and filter operations in one step to
		avoid having to iterate over the results twice.

		The graph is queried for the given (s,p,o) and we take
		the resulting triples and create an index and a mask.

		The index corresponds to the bitmat as described in
		the paper, having performed the filter operation.

		The mask is the result of the fold operation along the
		retained dimension, and can be used for bitwise AND
		operations for effecting a join.
		"""
		index = {}
		mask = BitVector()
		retain = int(retain)
		for triple in self.graph.triples((s,p,o), *av, **kw):
			triple_id = map(self.nodes.get_key, triple)
			rest = index.setdefault(triple_id[retain], {})
			mask[triple_id[retain]] = True
			if retain == SUBJECT:
				pred = rest.setdefault(triple_id[1], {})
				pred[triple_id[2]] = triple
			elif retain == PREDICATE:
				subj = rest.setdefault(triple_id[0], {})
				subj[triple_id[2]] = triple
			elif retain == OBJECT:
				subj = rest.setdefault(triple_id[0], {})
				subj[triple_id[1]] = triple
		return index, mask

	def unfold(self, index, mask):
		"""
		Return a generator of tuples that are still present
		in the index after applying the mask.
		"""
		i = 0
		for key in mask:
			rest = index[key]
			for n in rest:
				for m in rest[n]:
					yield rest[n][m]

	def join(self, filters):
		"""
		Perform a multiple join with the given filters and
		return a generator of (dimension, tuple) where dimension
		is the one that was used for partial join that generated
		that tuple.

		The filters argument is an iterable that should yield
		tuples of the form,

			(dimension, statement)

		where dimension is one of SUBJECT, PREDICATE or OBJECT
		and statement is to be used to filter the graph. For 
		example this set of filters,

		(
			(SUBJECT, (None, RDF.type, SWC["Paper"])),
			(SUBJECT, (None, RDFS.label, None)
		)

		is equivalent to the SPARQL query,

		SELECT * WHERE {
			?subject a swc:Paper .
			?subject rdfs:label ?label
		}
		"""
		mask = BitVector()
		mask.set()
		results = []
		for retain, filter in filters:
			r, m = self.fold(retain, filter)
			results.append((retain, r))
			mask = mask & m
		for retain, result in results:
			for statement in self.unfold(result, mask):
				yield retain, statement
