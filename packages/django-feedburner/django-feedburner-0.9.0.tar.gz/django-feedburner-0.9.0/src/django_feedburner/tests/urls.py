# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf.urls.defaults import *
from django_feedburner.tests.feeds import NumbersFeed


handler404 = 'django_feedburner.tests.urls.handle_404'

def handle_404(request):
    response = HttpResponse('404')
    response.status_code = 404
    return response


feed_dict = {
    'publicnumbers': NumbersFeed,
    'numbers': NumbersFeed,
}

urlpatterns = patterns('',
    url(r'^feeds/(?P<url>.*)/$', 'django_feedburner.views.redirected_feed',
        {'feed_dict': feed_dict}),
)
