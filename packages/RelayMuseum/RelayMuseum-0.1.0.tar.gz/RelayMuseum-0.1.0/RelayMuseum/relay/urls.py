from django.conf.urls.defaults import *

from relay.models import *

language_list = {
        'queryset': Language.objects.all(),
        'extra_context': { 'me': 'language', }
    }

participant_list = {
        'queryset': Participant.objects.all(),
        'extra_context': { 'me': 'participant', }
    }

urlpatterns = patterns('django.views.generic',
        (r'^language/(?P<slug>[-a-z0-9._]+)/$', 'list_detail.object_detail', dict(language_list)),
        (r'^language/$', 'list_detail.object_list', dict(language_list)),
        (r'^participant/(?P<slug>[-a-z0-9._]+)/$', 'list_detail.object_detail', dict(participant_list)),
)

urlpatterns += patterns('relay.views',
        (r'^relay/(?P<relay>[-a-z0-9._]+)/(?P<ring>[-a-z0-9._]+)/(?P<id>[0-9]+)/$', 'torch_detail'),
        (r'^relay/(?P<relay>[-a-z0-9._]+)/(?P<ring>[-a-z0-9._]+)/([?](?P<action>smooth))?$', 'show_ring'),
        (r'^relay/(?P<slug>[-a-z0-9._]+)/$', 'relay_detail'),
        (r'^relay/$', 'relay_list'),
        (r'^statistics/$', 'show_statistics'),
        (r'^participant/$', 'participant_list'),
)

