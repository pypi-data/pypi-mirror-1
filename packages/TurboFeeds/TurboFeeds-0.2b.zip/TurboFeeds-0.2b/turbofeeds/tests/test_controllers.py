# -*- coding: UTF-8 -*-

import datetime
import re
import unittest

from turbogears import config, controllers, expose, testutil, url
if not hasattr(testutil, 'TGTest'):
    raise ImportError("Sorry, you need at least TurboGears 1.1b1 to run the tests!")

from turbofeeds import FeedController, xml_stylesheet, __version__ as tf_version

data_entries = [
    dict(
        id = '1',
        updated = datetime.datetime.now(),
        published = datetime.datetime.now(),
        title = 'My first article',
        text = 'Humpty dumpty sat on the wall...'
    )
]

class TestFeedController(FeedController):

    def get_feed_data(self, **kwargs):
        entries = []
        for entry in data_entries:
            foo = {}
            foo["updated"] = entry['updated']
            foo["title"] = entry['title']
            foo["published"] = entry['published']
            foo["author"] = {"name": "John Doe", "email": "john@foo.org"}
            foo["link"] = 'http://blog.foo.org/article/%s' % entry['id']
            foo["summary"] = entry['text']
            entries.append(foo)
        return dict(
            title = "my fine blog",
            link = "http://blog.foo.org",
            author = {"name": "John Doe", "email": "john@foo.org"},
            id = "http://blog.foo.org",
            subtitle = "a blog about turbogears",
            entries = entries
        )

    @expose()
    def with_stylesheet(self):
        tg.redirect("%s" % self.default, stylesheet='/static/css/atom.css')


class TestRoot(controllers.RootController):

    feed = TestFeedController()

    @expose()
    def index(self):
        return dict()

banner = r"TurboFeeds FeedController \(%s, TG .*?, %s\)"
kid_generator_rx = re.compile(banner % (tf_version, 'kid'))
genshi_generator_rx = re.compile(banner % (tf_version, 'genshi'))

class TestKidFeedController(testutil.TGTest):
    root = TestRoot

    def setUp(self):
        super(TestKidFeedController, self).setUp()
        config.update({'tg.defaultview': 'kid'})

    def test_default_redirect(self):
        """Requesting the base url redirects correctly to the default handler."""
        response = self.app.get("/feed/", status=302)
        assert response.headers["Location"].endswith("/feed/%s" % self.root.feed.default)

    def test_kid_atom1_0_template(self):
        """The kid Atom 1.0 template renders without errors."""
        response = self.app.get("/feed/atom1_0", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/atom+xml")
        assert '<feed xmlns="http://www.w3.org/2005/Atom">' in response
        assert kid_generator_rx.search(response.body)

    def test_kid_atom0_3_template(self):
        """The kid Atom 0.3 template renders without errors."""
        response = self.app.get("/feed/atom0_3", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/atom+xml")
        assert '<feed version="0.3" xmlns="http://purl.org/atom/ns#">' in response
        assert kid_generator_rx.search(response.body)

    def test_kid_rss_template(self):
        """The kid RSS 2.0 template renders without errors."""
        response = self.app.get("/feed/rss2_0", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/rss+xml")
        assert '<rss version="2.0">' in response
        assert kid_generator_rx.search(response.body)

    def test_kid_mrss_template(self):
        """The kid MRSS 1.1.1 template renders without errors."""
        response = self.app.get("/feed/mrss1_1_1", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/rss+xml")
        assert 'xmlns:media="http://search.yahoo.com/mrss/"' in response
        assert kid_generator_rx.search(response.body)

class TestGenshiFeedController(testutil.TGTest):
    root = TestRoot

    def setUp(self):
        super(TestGenshiFeedController, self).setUp()
        config.update({'tg.defaultview': 'genshi'})

    def test_genshi_atom1_0_template(self):
        """The Genshi Atom 1.0 template renders without errors."""
        response = self.app.get("/feed/atom1_0", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/atom+xml")
        assert response.xml.tag == '{http://www.w3.org/2005/Atom}feed'
        assert genshi_generator_rx.search(response.body)

    def test_genshi_atom0_3_template(self):
        """The Genshi Atom 0.3 template renders without errors."""
        response = self.app.get("/feed/atom0_3", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/atom+xml")
        assert response.xml.get('version') == "0.3"
        assert response.xml.tag == '{http://purl.org/atom/ns#}feed'
        assert genshi_generator_rx.search(response.body)

    def test_genshi_rss_template(self):
        """The Genshi RSS 2.0 template renders without errors."""
        response = self.app.get("/feed/rss2_0", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/rss+xml")
        assert response.xml.get('version') == "2.0"
        assert response.xml.tag == 'rss'
        assert genshi_generator_rx.search(response.body)

    def test_genshi_mrss_template(self):
        """The Genshi MRSS 1.1.1 template renders without errors."""
        response = self.app.get("/feed/mrss1_1_1", status=200)
        print response
        assert response.headers["Content-Type"].startswith(
            "application/rss+xml")
        assert response.xml.get('version') == "2.0" and response.xml.tag == 'rss'
        assert 'xmlns:media="http://search.yahoo.com/mrss/"' in response
        assert genshi_generator_rx.search(response.body)
