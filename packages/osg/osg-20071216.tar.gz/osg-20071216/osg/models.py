from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.gis.db import models
from django.conf import settings

from feedback import GenerativeFeedbackManager
from fields import UniqueIdField

class Node(models.Model):
	"""
	Uniquely identifiable node for use in a directed graph.

	This uses the special manager, FeedbackManager, to make
	possible the generation of sample networks for experiments
	according to the model of Farmer et al.
	"""
	created = models.DateTimeField(auto_now_add=True,
			verbose_name=_('created'))
	uniqueid = UniqueIdField(verbose_name=_('unique'))
	objects = GenerativeFeedbackManager()
	class Meta:
		verbose_name = _('node')
		verbose_name_plural = _('nodes')
	def __str__(self):
		return self.uniqueid
	def outdegree(self):
		"returns the number of links out from this node"
		return self.out_set.count()
	def indegree(self):
		"returns the number of links in to this node"
		return self.in_set.count()
	def neighbours(self):
		"returns the set of adjacent (out) nodes"
		return map(lambda x: x.dst, self.out_set.all())
	def link(self, node):
		"create an outbound link to the given node"
		if node == self:
			raise ValueError('%s and %s are the same!' % (self, node))
		edge, created = Edge.objects.get_or_create(src=self, dst=node)
		return edge

class Edge(models.Model):
	"""
	An edge connecting two nodes in a directed graph.
	"""
	created = models.DateTimeField(auto_now_add=True,
				verbose_name=_('created'))
	src = models.ForeignKey(Node, related_name='out_set',
				verbose_name=_('source'))
	dst = models.ForeignKey(Node, related_name='in_set',
				verbose_name=_('destination'))
	class Meta:
		verbose_name = _('edge')
		verbose_name_plural = _('edges')

###
### Node Meta-Data
###
class Email(models.Model):
	created = models.DateTimeField(auto_now_add=True,
				verbose_name=_('created'))
	node = models.ForeignKey(Node, related_name='email_set',
				verbose_name=_('node'))
	email = models.EmailField(maxlength=256, unique=True,
				verbose_name=_('email'))
	class Meta:
		ordering = ('node', 'email')
	def __str__(self):
		return self.email

class Name(models.Model):
	created = models.DateTimeField(auto_now_add=True,
				verbose_name=_('created'))
	node = models.ForeignKey(Node, related_name='name_set',
				verbose_name=_('node'))
	name = models.CharField(maxlength=1024,
				verbose_name=_('name'))
	class Meta:
		verbose_name=_('name')
		verbose_name_plural=_('names')
		ordering = ('node', 'name')
		unique_together = (('node', 'name'),)
	def __str__(self):
		return self.name

class Location(models.Model):
	created = models.DateTimeField(auto_now_add=True,
				verbose_name=_('created'))
	node = models.ForeignKey(Node, related_name='location_set',
				verbose_name=_('node'))
	location = models.PointField(verbose_name=_('location'))
	objects = models.GeoManager()
	class Meta:
		verbose_name=_('location')
		verbose_name_plural=_('locations')
