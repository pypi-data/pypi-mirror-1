# -*- coding: UTF-8 -*-
"""TurboFeed controllers for RSS/Atom feeds handling."""
__docformat__ = 'restructuredtext'

__all__ = [
    'FeedController',
]

__version__ = '1.1'

import logging

import turbogears

from util import xml_stylesheet, absolute_url


log = logging.getLogger('turbofeeds.controllers')


class FeedController(turbogears.controllers.Controller):
    """Controller for generating feeds in multiple formats.

    Must be subclassed and a ``get_feed_data`` method provided that returns
    a dict with the feed info (see constructor doc strings) and an ``entries``
    member, which should be a list filled with dicts each representing a feed
    entry (see docstring for the default implementation).
    """

    formats = ["atom1.0", "atom0.3", "rss2.0"]

    # Constructor / Intialisation
    def __init__(self, default="atom1.0", base_url='/feed', **feed_params):
        """Constructor - Should be called with ``super()`` if overwritten.

        The ``default`` arguments sets the default feed format when the
        feed base URL is requested. Currently supported values are
        ``atom1_0`` (the default), ``atom0_3`` and ''rss1_0``.

        The ``base_url`` sets the URL where the feed controller is mounted
        to the CherryPy object tree. The default is '/feed'. This is used
        to construct the full feed URL for the ``link`` element in the feed,
        if it is not overwritten by the ``link`` keyword argument.

        Any extra keyword arguments will be assigned to the ``feed_params``
        attribute and added to the feed data everytime a feed is requested.
        This can be used to set the feed info in the direct child elements
        of the ``feed`` (Atom) resp. ``channel`` root element of the feed.
        Possible names include:

        * author (dict with ``name``, ``email`` and ``uri`` members)
        * categories (list of strings, used by Atom 1.0 / RSS only)
        * generator (string)
        * updated (datetime)
        * icon (URL, used by Atom 1.0 format only)
        * id (string/URL, used by Atom formats only)
        * logo (URL, used by Atom 1.0 / RSS format only)
        * lang (string, used by RSS format only)
        * link (URL)
        * rights (string)
        * subtitle (string)
        * stylesheet (URL or dict with members ``href`` and ``type`` or a
          calable returning either, used place a matching xml-stylesheet 
          processing instruction at the top of the feed XML)
        * title (string)

        For up-to-date information about supported elements and values, please
        refer to the templates for the different feed formats in the
        ``templates`` sub-package.
        """

        super(FeedController, self).__init__()
        assert default in self.formats
        self.default = default
        self.base_url = base_url
        self.feed_params = feed_params

    # Exposed methods
    @turbogears.expose()
    def index(self, *args, **kwargs):
        """Redirects to the default feed format rendering method."""

        turbogears.redirect(turbogears.url("%s" % self.default), kwargs)

    @turbogears.expose(template="turbofeeds.templates.atom0_3",
        format="xml", content_type="application/atom+xml")
    def atom0_3(self, *args, **kwargs):
        """Renders Atom 0.3 XML feed."""

        feed = self.init_feed()
        feed.update(self.get_feed_data(*args, **kwargs))
        self.format_dates(feed, 3339)
        feed.setdefault('link', self.get_feed_url("atom0_3", *args, **kwargs))
        log.debug(feed)
        return feed

    @turbogears.expose(template="turbofeeds.templates.atom1_0",
        format="xml", content_type="application/atom+xml")
    def atom1_0(self, *args, **kwargs):
        """Renders Atom 1.0 XML feed."""

        feed = self.init_feed()
        feed.update(self.get_feed_data(*args, **kwargs))
        self.format_dates(feed, 3339)
        feed.setdefault('link', self.get_feed_url("atom1_0", *args, **kwargs))
        log.debug(feed)
        return feed

    @turbogears.expose(template="turbofeeds.templates.rss2_0",
        format="xml", content_type="application/rss+xml")
    def rss2_0(self, *args, **kwargs):
        """Renders RSS 2.0 XML feed."""

        feed = self.init_feed()
        feed.update(self.get_feed_data(*args, **kwargs))
        self.format_dates(feed, 822)
        feed.setdefault('link', self.get_feed_url("rss2_0", *args, **kwargs))
        log.debug(feed)
        return feed

    # Helper methods
    def date_to_3339(self, date):
        """Converts datatime object to RFC 3339 string representation."""

        date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return date

    def date_to_822(self, date):
        """Converts datatime object to RFC 822 string representation."""

        date = date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return date

    def format_dates(self, feed, format):
        """Converts datetime objects in the feed data into given format."""

        if format == 822:
            convert_date = self.date_to_822
        else:
            convert_date = self.date_to_3339
        for field in ('published', 'updated'):
            if field in feed:
                feed[field] = convert_date(feed[field])

        for entry in feed['entries']:
            for field in ('published', 'updated'):
                if field in entry:
                    entry[field] = convert_date(entry[field])
        return feed

    def get_feed_data(self, *args, **kwargs):
        """Returns dict with feed info and a list of feed entries.

        This method must be overwritten by a subclass.

        It should return a dictionary with members for the feed info (see the
        constructor doc string) and a member ``entries``, which is a list with
        dict items for each feed entry. Supported members in each dict include:

        * author (dict with ``name``, ``email`` and ``uri`` members)
        * categories (list of strings, used by Atom 1.0 / RSS only)
        * content (string or dict with ``type`` and ``value`` members,
          Atom formats only)
        * updated (datetime, Atom only)
        * id (string/URL, Atom only)
        * link (URL)
        * published (datetime)
        * rights (string, Atom 1.0 only)
        * summary (string)
        * title (string)

        For up-to-date information about supported elements and values, please
        refer to the templates for the different feed formats in the
        ``templates`` sub-package.
        """

        raise NotImplementedError

    def get_feed_url(self, version='atom1_0', *args, **kwargs):
        """Returns absolute URL (including server name) for the feed."""

        if not self.base_url.endswith('/'):
            base_url = self.base_url + '/'
        else:
            base_url = self.base_url + '/'
        if args:
            suffix = '/' + '/'.join([str(a) for a in args])
        else:
            suffix = ''
        feed_url = absolute_url('%s%s%s' %
          (base_url, version, suffix), **kwargs)
        return feed_url

    def init_feed(self):
        """Initializes feed data with the kwargs given to the constructor."""

        feed = {
            'xml_stylesheet': xml_stylesheet,
            'generator': 'TurboFeeds FeedController version %s' % __version__
        }
        feed.update(self.feed_params)
        return feed
