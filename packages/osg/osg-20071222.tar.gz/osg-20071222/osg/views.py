from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.xmlutils import SimplerXMLGenerator
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site
from django import newforms as forms
from django.conf import settings
from datetime import datetime
from osg.models import Node

namespaces = {
	'xmlns' : 'http://www.w3.org/2005/Atom',
	'xmlns:georss' : 'http://www.georss.org/georss',
	'xmlns:gd' : 'http://schemas.google.com/g/2005',
}

def get_node_or_404(guid):
	try: 
		return Node.objects.get(uniqueid = guid)
	except Node.DoesNotExist:
		raise Http404

def node_uri(node):
	site = Site.objects.get(pk=settings.SITE_ID)
	return 'http://%s/feeds/people/%s/' % (site.domain, node.uniqueid)

def node_name(node):
	names = map(str, node.name_set.all())
	return '\n'.join(names)

def person(request, guid):
	"""
	Support for OpenSocial Person API 
	http://code.google.com/apis/opensocial/docs/gdata/people/developers_guide_protocol.html#GettingPerson
	"""
	node = get_node_or_404(guid)
	response = HttpResponse(mimetype='text/xml')
	handler = SimplerXMLGenerator(response, 'utf-8')
	entry(handler, node, namespaces)
	return response

def friends(request, guid):
	"""
	Support for OpenSocial Friends API
	http://code.google.com/apis/opensocial/docs/gdata/people/developers_guide_protocol.html#RetrievingFriends
	"""
	node = get_node_or_404(guid)
	response = HttpResponse(mimetype='text/xml')
	handler = SimplerXMLGenerator(response, 'utf-8')

	handler.startElement(u'feed', namespaces)

	uri = node_uri(node)
	handler.addQuickElement(u'id', uri + 'friends/')

	updated = datetime.utcnow().isoformat() + '-00:00'
	handler.addQuickElement(u'updated', updated)

	handler.addQuickElement(u'title', _('friends'))

	name = node_name(node)
	if name:
		handler.startElement(u'author', {})
		handler.addQuickElement(u'name', name)
		handler.endElement(u'author')

	for neighbour in node.neighbours():
		entry(handler, neighbour)

	handler.endElement(u'feed')

	return response

def entry(handler, node, namespaces = {}):
	handler.startElement(u'entry', namespaces)

	uri = node_uri(node)
	handler.addQuickElement(u'id', uri)

	updated = datetime.utcnow().isoformat() + '-00:00'
	handler.addQuickElement(u'updated', updated)

	title = node_name(node)
	if title:
		handler.addQuickElement(u'title', title)

	link_self_attrs = {
		'rel' : 'self',
		'type' : 'application/atom+xml',
		'href' : uri,
	}
	handler.addQuickElement(u'link', u'', link_self_attrs)

	handler.endElement(u'entry')

