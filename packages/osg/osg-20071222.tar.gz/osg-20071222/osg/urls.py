from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^feeds/people/([^/]+)/$', 'osg.views.person'),
	(r'^feeds/people/([^/]+)/friends/$', 'osg.views.friends')
)
