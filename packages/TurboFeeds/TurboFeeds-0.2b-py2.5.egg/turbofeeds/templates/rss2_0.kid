<?xml version="1.0" encoding="utf-8"?>
<root xmlns:py="http://purl.org/kid/ns#" py:strip="">
<div py:replace="xml_stylesheet(stylesheet)" py:if="value_of('stylesheet')" />
<rss version="2.0">
<channel>

  <generator py:if="defined('generator')" py:content="generator">
    feed generator
  </generator>
  <title py:if="defined('title')" py:content="title">
    feed title
  </title>
  <link py:if="defined('link')" py:content="link">
    feed link
  </link>
  <lastBuildDate py:if="defined('updated')" py:content="updated">
    feed modification timestamp
  </lastBuildDate>
  <managingEditor py:if="defined('author') and 'email' in author" py:content="author['email']">
    feed author email
  </managingEditor>
  <pubDate py:if="defined('published')" py:content="published">
    feed publication timestamp
  </pubDate>
  <image py:if="defined('logo')">
    <url py:content="logo">
      logo image url
    </url>
    <title py:if="defined('title')" py:content="title">
      logo image title
    </title>
    <link  py:if="defined('link')" py:content="link">
      logo image link url
    </link>
  </image>
  <copyright py:if="defined('rights')" py:content="rights">
    feed rights
  </copyright>
  <language py:if="defined('lang')" py:content="lang">
    feed language
  </language>
  <description py:if="defined('subtitle')" py:content="subtitle">
    feed description
  </description>
  <category py:for="cat in value_of('categories', [])" py:content="cat" />

  <item py:for="entry in entries">
    <guid py:if="'id' in entry" py:content="entry['id']">
      entry guid
    </guid>
    <title py:if="'title' in entry" py:content="entry['title']">
      entry title
    </title>
    <link py:if="'link' in entry" py:content="entry['link']">
      entry link
    </link>
    <pubDate py:if="'published' in entry" py:content="entry['published']">
      entry publication timestamp
    </pubDate>
    <author py:if="'author' in entry and 'email' in entry['author']" py:content="entry['author']['email']">
      entry author email
    </author>
    <description py:if="'summary' in entry" py:content="entry['summary']">
      entry description
    </description>
    <category py:for="cat in entry.get('categories', [])" py:content="cat" />
  </item>

</channel>
</rss>
</root>
