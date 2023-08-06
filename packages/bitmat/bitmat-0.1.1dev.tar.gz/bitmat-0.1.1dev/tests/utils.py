from rdflib.term import URIRef as _URIRef, Literal as _Literal
from rdflib.graph import Graph
from datetime import datetime
from sys import stdout

class URIRef(_URIRef):
	def __repr__(self):
		return "U"
class Literal(_Literal):
	def __repr__(self):
		return "L"

def time(func, n=10):
	def _t(*av, **kw):
		if av:
			if len(av) == 1 and isinstance(av[0], tuple):
				stdout.write("%s... " % (av[0],))
			else:
				stdout.write("%s... " % (av,))
		stdout.write("%d reps... " % (n,))
		start = datetime.now()
		for i in range(n):
			result = func(*av, **kw)
		end = datetime.now()
		delta = (end - start) / n
		stdout.write("%s... " % (delta,))
		stdout.flush()
		return result
	return _t

def permute_statement((s,p,o)):
	yield (None, None, None)
	yield (s, None, None)
	yield (None, p, None)
	yield (None, None, o)
	yield (s, p, None)
	yield (s, None, o)
	yield (None, p, o)
	yield (s, p, o)

