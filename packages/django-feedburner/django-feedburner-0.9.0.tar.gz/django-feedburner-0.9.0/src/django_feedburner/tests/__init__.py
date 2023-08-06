# -*- coding: utf-8 -*-
from django.test import Client, TestCase


class TestRedirectFeedView(TestCase):
    def setUp(self):
        self.feedburner = Client(HTTP_USER_AGENT='FeedBurner 1.0')

    def test_redirect(self):
        response = self.client.get('/feeds/numbers/')
        self.assertEqual(response.status_code, 301)

        # allow access for feedburner useragent
        response = self.feedburner.get('/feeds/numbers/')
        self.assertEqual(response.status_code, 200)

        # no redirect if this feed is not configured in settings
        response = self.client.get('/feeds/publicnumbers/')
        self.assertEqual(response.status_code, 200)

    def test_not_existend_feed(self):
        response = self.client.get('/feeds/wrongfeed/')
        self.assertEqual(response.status_code, 301)

        # feed not in feedburner settings
        response = self.client.get('/feeds/wrongfeed2/')
        self.assertEqual(response.status_code, 404)
