# -*- coding: utf-8 -*-
from django.http import HttpResponsePermanentRedirect
from django.contrib.syndication.views import feed as syndication_feed
from django.conf import settings


if not hasattr(settings, 'FEEDBURNER_URL_PREFIX'):
    settings.FEEDBURNER_URL_PREFIX = 'http://feeds.feedburner.com'
if not hasattr(settings, 'FEEDBURNER_URLS'):
    settings.FEEDBURNER_URLS = {}


for key, value in settings.FEEDBURNER_URLS.items():
    if value.startswith('/'):
        settings.FEEDBURNER_URLS[key] = settings.FEEDBURNER_URL_PREFIX + value


def redirected_feed(request, *args, **kwargs):
    # if requested by feedburner we will return the original feed url
    if request.META.get('HTTP_USER_AGENT', '').startswith('FeedBurner') or \
        request.path not in settings.FEEDBURNER_URLS:
        return syndication_feed(request, *args, **kwargs)
    return HttpResponsePermanentRedirect(settings.FEEDBURNER_URLS[request.path])
