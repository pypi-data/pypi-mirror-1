from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

STATIC_DOC_ROOT = settings.SITE_ROOT + '/media'

urlpatterns = patterns('',
    (r'^admin/doc/',            include('django.contrib.admindocs.urls')),
#    (r'^admin/webalizer/',      include('webalizer.urls')),
    (r'^admin/(.*)',            admin.site.root),
    (r'^$',          'django.views.generic.simple.direct_to_template',
    {'template': 'index.html', 'extra_context': {'me': 'home'}}),
    (r'^',          include('relay.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$',   'django.views.static.serve', {'document_root': STATIC_DOC_ROOT }),
    )


