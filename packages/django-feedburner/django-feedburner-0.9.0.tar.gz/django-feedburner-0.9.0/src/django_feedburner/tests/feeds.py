# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed


class NumbersFeed(Feed):
    title = 'numbers'
    link = '/'
    description = 'counting numbers'

    def items(self):
        return range(25)

    def item_title(self, obj):
        return 'Number %s' % obj
    item_description = item_title

    def item_link(self, obj):
        return '/%s' % obj
