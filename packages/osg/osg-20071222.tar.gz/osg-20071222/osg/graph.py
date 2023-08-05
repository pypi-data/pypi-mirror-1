from django.db import models
from networkx.digraph import DiGraph

class EdgeManager(models.Manager):
	def graph(self, *av, **kw):
		g = DiGraph()
		for edge in self.filter(*av, **kw):
			g.add_edge(edge.src.id, edge.dst.id)
		return g
