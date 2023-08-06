from django.views.generic.list_detail import object_list, object_detail

from relay.models import *

from nano.tools import render_page

def in_kwargs_or_get(request, kwargs, key, value):
    """If an url has the key-value-pair key=<value> in kwargs or
    the key <value> in GET, return the value, else return False."""
    assert value, '"value" cannot be empty/false'
    if kwargs.get(key, '') == value or value in request.GET:
        return True
    return False

def show_ring(request, *args, **kwargs):
    if in_kwargs_or_get(request, kwargs, u'action', 'smooth'):
        return torch_smooth_translation_list(request, *args, **kwargs)
    return torch_list(request, *args, **kwargs)

def torch_list(request, *args, **kwargs):
    relay = Relay.objects.get(slug=kwargs['relay'])
    ring = Ring.objects.get(relay=relay, slug=kwargs['ring'])
    queryset = Torch.objects.filter(ring=ring).order_by('pos')
    extra_context = {
        'me': 'relay',
        'ring': ring,
        'relay': relay,
    }
    return object_list(request, queryset, extra_context=extra_context)

def relay_list(request, *args, **kwargs):
    queryset = Relay.objects.order_by('pos')
    extra_context = {
        'me': 'relay',
    }
    return object_list(request, queryset, extra_context=extra_context)

def participant_list(request, *args, **kwargs):
    queryset = Participant.objects.all()
    extra_context = {
        'me': 'participant',
        'relay_masters': queryset.filter(relay_mastering__isnull=False).distinct(),
        'ring_masters': queryset.filter(ring_mastering__isnull=False).distinct(),
    }
    return object_list(request, queryset, extra_context=extra_context)

def torch_smooth_translation_list(request, *args, **kwargs):
    relay = Relay.objects.get(slug=kwargs['relay'])
    ring = Ring.objects.get(relay=relay, slug=kwargs['ring'])
    queryset = Torch.objects.filter(ring=ring).order_by('pos')
    extra_context = {
        'me': 'relay',
        'ring': ring,
        'relay': relay,
    }

    return object_list(request, 
            queryset, 
            template_name='relay/ring_smooth_translation.html',
            extra_context=extra_context)

def relay_detail(request, *args, **kwargs):
    relay = Relay.objects.get(slug=kwargs['slug'])
    rings = Ring.objects.filter(relay=relay)
    queryset = Relay.objects.all()
    extra_context = {
        'me': 'relay',
        'rings': rings,
        'num_rings': rings.count(),
        'relay': relay,
    }

    return object_detail(request, queryset, object_id=relay.id, extra_context=extra_context)

def torch_detail(request, *args, **kwargs):
    relay = Relay.objects.get(slug=kwargs['relay'])
    ring = Ring.objects.get(relay=relay, slug=kwargs['ring'])
    queryset = Torch.objects.filter(ring=ring, id=kwargs['id'])
    torch = queryset[0]
    extra_context = {
        'me': 'relay',
        'ring': ring,
        'relay': relay,
    }

    return object_detail(request, queryset, object_id=torch.id, extra_context=extra_context)

def show_statistics(request, *args, **kwargs):
    num_langs = Language.objects.count()
    num_participants = Participant.objects.count()
    num_relays = Relay.objects.count()
    num_rings = Ring.objects.count()
    num_torches = sum(relay.num_torches for relay in Relay.objects.filter(missing=False))

    avg_rings_per_relay = (num_rings - 1) / float(num_relays - Relay.objects.filter(missing=True).count())
    avg_torches_per_ring = float(num_torches) / num_rings - 1
    avg_torches_per_relay = float(num_torches) / num_relays
    avg_participants_per_language = num_participants / float(num_langs)
    if CalsLanguage:
        avg_calslanguages = Language.objects.filter(cals_language__isnull=False).count() / float(num_langs) * 100
    else:
        avg_calslanguages = None
    avg_calsparticipants = Participant.objects.filter(cals_user__isnull=False).count() / float(num_participants) * 100

    all_missing_torches = sum(relay.missing_torches for relay in Relay.objects.all())
    all_missing_relays = Relay.objects.filter(missing=True)

    langstats = {
            'num': num_langs,
            'avg_participants': avg_participants_per_language,
            'avg_calslang': avg_calslanguages,
    }
    participantstats = {
            'num': num_participants,
            'avg_calsuser': avg_calsparticipants,
    }
    relaystats = {
            'num': num_relays,
            'avg_rings': avg_rings_per_relay,
            'avg_torches': avg_torches_per_relay,
            'avg_torches_per_ring': avg_torches_per_ring,
    }
    missingstats = {
            'torches': all_missing_torches,
            'relays': all_missing_relays,
    }
    data = {'relay': relaystats,
            'lang': langstats,
            'participant': participantstats,
            'missing': missingstats,
            'me': 'statistics',
            }

    return render_page(request, 'relay/statistics.html', data)
