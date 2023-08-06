# Release information about TurboFeeds
# -*- coding: UTF-8 -*-
"""TurboGears controller and widgets for feed handling.

Turbofeeds is a TurboGears_ 1 extension which provides support for generating
RSS and Atom feeds and matching display widgets.

TurboFeeds was formerly the ``feed`` sub-package of the main TurboGears
distribution. It was extracted from the TG core to ease updating, enhancing,
and maintaining both projects.

TurboFeeds is mostly backwards-compatible with the ``turbogears.feed``
package, but has lots of fixes and a few new features, most importantly support
for Genshi templates. It works with both the TurboGears 1.x and the 1.1 branch.


Installation
------------

To install TurboFeeds from the Cheeseshop_ use `easy_install`_::

    [sudo] easy_install TurboFeeds

This requires the setuptools_ package to be installed. If you have not done so
already, download the `ez_setup.py`_ script and run it to install setuptools.

If you want to get the latest development version, you can check out the
trunk from the `Subversion repository`_ with::

    svn co http://svn.turbogears.org/projects/TurboFeeds/trunk TurboFeeds

For bug reports and feature requests, please go to the TurboGears trac at
http://trac.turbogears.org/.

To open a ticket, you'll need a trac account. Please select "TurboFeeds" as the
ticket component.


Usage
-----

Controller::

    from turbogears import controllers, expose
    from turbofeeds import FeedController, FeedHeadLinks, FeedLinks

    class MyFeedController(FeedController):
        def get_feed_data(self, **kwargs):
            entries = []
            # Fill ``entries`` with dicts containing at least items for:
            #
            #   title, link, summary and published
            #
            # For example, supposing ``entry`` is a database object
            # representing a blog article:
            entries.append(dict(
                title = entry.title,
                author = dict(name = entry.author.display_name,
                    email = entry.author.email_address),
                summary = entry.post[:30],
                published = entry.published,
                updated = entry.updated or entry.published,
                link = 'http://blog.foo.org/article/%s' % entry.id
            ))
            return dict(entries=entries)

    class Root(controllers.RootController):
        feed = MyFeedController(
            base_url = '/feed',
            title = "my fine blog",
            link = "http://blog.foo.org",
            author = dict(name="John Doe", email="john@foo.org"),
            id = "http://blog.foo.org",
            subtitle = "a blog about turbogears"
        )
        feedlheadinks = FeedHeadLinks(controller=feed)
        feedlinks = FeedLinks(controller=feed,
            title = "Click link to access the feed in %(type)s format")

        @expose('.templates.mypage')
        def mypage(self):
            return dict(
                feedheadlinks=self.feedheadlinks,
                feedlinks=self.feedlinks)

Template::

    <head>
      ${feadheadlinks()}
      ...
    </head>
    <body>
      <h2>Feed links</h2>
      ${feedlinks('%(type)s feed', url_params=dict(format='full'))}
      ...
    </body>


Documentation
-------------

The TurboFeeds source is thoroughly documented with doc strings.
The source distribution comes with epydoc-generated `API documentation`_
included.

You can also refer to the documentation for the original ``turbogears.feed``
package on the TurboGears documentation wiki:

    http://docs.turbogears.org/1.0/FeedController

All information on this page is also still valid for TurboFeeds, you
just have to replace::

    from turbogears.feed import FeedController

with::

    from turbofeeds import FeedController

Credits
-------

* The ``turbogears.feed`` package was first introduced in TurboGears version
  0.9a1 and was added by Elvelind Grandin.

* Christopher Arndt turned it into the TurboGears extension TurboFeeds.

* Other contributors include:

  Florent Aide, Simon Belak, Kevin Dangoor, Charles Duffy, Alberto Valverde,
  Jorge Vargas

  Please notify the maintainer, if you think your name should belong here too.

* The feed icons used by the CSS for the FeedLinks widget where taken from
  http://www.feedicons.com/.


.. _turbogears: http://www.turbogears.org/
.. _cheeseshop: http://cheeseshop.python.org/pypi/TurboFeeds
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
.. _api documentation: http://chrisarndt.de/projects/turbofeeds/api/index.html
.. _subversion repository:
    http://svn.turbogears.org/projects/TurboFeeds/trunk#egg=turbofeeds-dev

"""
__docformat__ = 'restructuredtext'

name = "TurboFeeds"
version = "0.2b"
date = "$Date: 2009-09-27 05:36:36 +0200 (Sun, 27. Sep 2009) $"

_doclines = __doc__.split('\n')
description = _doclines[0]
long_description = '\n'.join(_doclines[2:])
author = "Elvelind Grandin, Christopher Arndt"
author_email = "chris@chrisarndt.de"
maintainer = "Christopher Arndt"
maintainer_email = "chris@chrisarndt.de"
copyright = "(c) 2006 - 2009 Elvelind Grandin et al."
license = "MIT license"

url = "http://chrisarndt.de/projects/turbofeeds"
download_url = "http://cheeseshop.python.org/pypi/TurboFeeds"
