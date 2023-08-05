# -*- coding: UTF-8 -*-
"""TurboFeed widgets for RSS/Atom feeds handling."""
__docformat__ = 'restructuredtext'

__all__ = [
    'FeedLinks',
    'FeedLinksDesc',
    'js_dir',
]

import logging

import pkg_resources

from turbogears import url
from turbogears.widgets import CSSLink, Widget, WidgetDescription, \
    register_static_directory


log = logging.getLogger('turbofeeds.widgets')

static_dir = pkg_resources.resource_filename("turbofeeds", "static")
register_static_directory("turbofeeds", static_dir)


class FeedLinks(Widget):
    """A list of links to feeds for all supported formats.
    
    value is the link text. May use "%(type)s" placeholder 
    for the feed format name.
    """

    params = ['base_url', 'controller', 'feed_types', 'title', 'url_params']
    template = """\
<div xmlns:py="http://purl.org/kid/ns#" py:strip="">
  <ul class="feedlinklist">
    <li py:for="type, name in feed_types">
      <a py:attrs="dict(title=title % dict(type=name))" class="feedlink"
        href="${feed_url(type)}">${value % dict(type=name)}</a>
    </li>
  </ul>
</div>
"""
    css = [CSSLink("turbofeeds", "css/feeds.css", media="screen")]
    base_url = None
    controller = None
    feed_types = [('rss2_0', 'RSS 2.0'), ('atom0_3', 'Atom 0.3'),
        ('atom1_0', 'Atom 1.0')]
    title = ''
    url_params = {}

    params_doc = {
        'base_url': 'The base_url of the feed. The feed format will be '
            'appended to this. Can be determined from "controler", if given.',
        'controller': 'The FeedController instance serving the feeds the '
            'links will point to.',
        'feed_types': 'A list of 2-item tuples matching format identifier to '
            'format name. A link will be generated for each format.',
        'title': 'String to use for "title" attribute of feed links. May use '
            '"%(type)s" placeholder for the feed format name.',
        'url_params' : 'Dictionary containing extra URL parameters appended to'
            ' the feed URL',
    }

    def update_params(self, params):
        """Sets feed URL to callable that generates URL for each format."""

        super(FeedLinks, self).update_params(params)
        base_url = params.get('base_url')
        if base_url is None:
            try:
                base_url = params['controller'].base_url
                log.debug('FeedController root URL: %s', base_url)
            except (KeyError, AttributeError):
                raise ValueError("You must set 'base_url' or 'controller'.")
        params['feed_url'] = lambda type: self.feed_url(
            base_url, type, params['url_params'])

    def feed_url(self, base_url, type, params):
        """Returns feed URL by combining base_url, feed type and params."""

        return url("%s/%s" % (base_url, type), params)


class FeedLinksDesc(WidgetDescription):
    name = "Feed link list"
    for_widget = FeedLinks(base_url = '/feed')
    template = """
    <div>
        ${for_widget("Subscribe to %(type)s feed", 
          title="Click link to access the feed in %(type)s format")}
    </div>
    """


if __name__ == '__main__':
    fl = FeedLinks()
    print fl.render('View %(type)s feed')
    print
    print fl.render('View %(type)s feed', title='Click to view feed in browser',
      url_params=dict(compat=True))
    fl = FeedLinks(base_url='/myfeeds')
    print fl.render('View my %(type)s feed')
