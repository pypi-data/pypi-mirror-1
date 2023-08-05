<?xml version="1.0" encoding="utf-8"?>
<root xmlns:py="http://purl.org/kid/ns#" py:strip="">
<div py:replace="xml_stylesheet(stylesheet)" py:if="defined('stylesheet')" />
<feed version="0.3" xmlns="http://purl.org/atom/ns#">

  <generator py:if="defined('generator')" py:content="generator">
    feed generator
  </generator>
  <id py:content="id">
    feed id
  </id>
  <title py:if="defined('title')" py:content="title">
    feed title
  </title>
  <modified py:if="defined('updated')" py:content="updated">
    feed modification timestamp
  </modified>
  <author py:if="defined('author')">
    <name py:content="author['name']">
      feed author name
    </name>
    <email py:if="'email' in author" py:content="author['email']">
      feed author email
    </email>
    <uri py:if="'uri' in author" py:content="author['uri']">
      feed author uri
    </uri>
  </author>
  <link py:if="defined('link')" rel="alternate" href="${link}" />
  <copyright py:if="defined('rights')" py:content="rights">
    feed copyright
  </copyright>
  <tagline py:if="defined('subtitle')" py:content="subtitle">
    feed tagline
  </tagline>

  <entry py:for="entry in entries">
    <id py:if="'id' in entry" py:content="entry['id']">
      entry id
    </id>
    <title py:if="'title' in entry" py:content="entry['title']">
      entry title
    </title>
    <link py:if="'link' in entry" rel="alternate" href="${entry['link']}" />
    <modified py:if="'updated' in entry" py:content="entry['updated']">
      entry modification timestamp
    </modified>
    <issued py:if="'published' in entry" py:content="entry['published']">
      entry issued timestamp
    </issued>
    <author py:if="'author' in entry">
        <name py:content="entry['author']['name']">
          entry author name
        </name>
        <email py:if="'email' in entry['author']" py:content="entry['author']['email']">
          entry author email
        </email>
        <uri py:if="'uri' in entry['author']" py:content="entry['author']['uri']">
          entry author uri
        </uri>
    </author>
    <content py:if="isinstance(entry.get('content'), dict)"
      py:content="entry['content']['value']"
      py:attrs="dict(type=entry['content'].get('type'))">
      entry content
    </content>
    <content py:if="'content' in entry and not isinstance(entry['content'], dict)"
      py:content="entry['content']">
      entry content
    </content>
    <summary py:if="'summary' in entry" py:content="entry['summary']">
      entry summary
    </summary>
  </entry>

</feed>
</root>
