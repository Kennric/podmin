<channel>
  <title> feed.title
  <link> feed.link
  <description> feed.summary
  <generator> feed.generator
  <docs> feed.docs
  <language> feed.language
  <copyright> feed.rights
  <managingEditor> feed.author
  <webmaster> feed.author
  <pubDate> feed.updated_parsed
  <lastBuildDate> feed.updated_parsed
  <ttl> feed.ttl
  <image> 
    <url> feed.image.href
    <title> feed.title
    <link> feed.link
    <description> feed.summary
  <atom:link 
    href= feed.links where type = application/rss+xml
  <itunes
    :author>  feed.author
    :subtitle> feed.subtitle
    :summary> feed.summary
    :owner>
      :name> feed.author_detail.name
      :email> feed.author_detail.email
    :block> feed.itunes_block
    :category (each feed.tags)
      text="">
      :category text="" />
    :keywords> feed.itunes_keywords
    :explicit> feed.itunes_explicit

  <item> (entries.each)
    <title> entry.title
    <link> entry.link
    <description> entry.summary (or content.value, html stripped)
    <author> entry.author
    <pubDate> entry.updated(parsed)
    <category> entry.tags (each)
    <comments> entry.comments
    <enclosure 
      url=entry.links.x (where rel = enclosure)
      length= entry.links.x.length
      type= entry.links.x.type
    />
    <guid isPermalink=entry.guidislink >entry.id</guid>
    <itunes:
       author> entry.author
       subtitle> entry.subtitle
       summary> entry.summary (or content.value, html stripped)
       explicit> entry.itunes_explicit
       duration> entry.itunes_duration
  </item>


  'entries': [
    {'summary_detail': {
      'base': u'http://leoville.tv/podcasts/fc.xml', 'type': 'text/html', 'value': u'<p><img align="right" border="0" hspace="20" src="http://leoville.tv/podcasts/coverart/fc144.jpg" title="FourCast" vspace="20" /></p>\n\n<p><b>Hosts:</b> <a href="http://tommerritt.com">Tom Merritt</a> and <a href="http://frogpants.com/">Scott Johnson</a></p>\n\n<p>We wear our computers, improve our toilets and all die in a singularity. But we can think our way out of it.</p>\n\n<p><b>Guests:</b> <a href="http://linkedin.com/in/dorseygraphics">Steve Dorsey</a> and <a href="http://twitter.com/PDelahanty">Patrick Delahanty</a>  </p>\n\n<p>Download or subscribe to this show at <a href="http://twit.tv/fc">twit.tv/fc</a>.</p>\n\n<p>Got a prediction of your own? Guest you\'d like to see? Question for the show? Email us at <a href="mailto: fourcastpodcast@gmail.com">fourcastpodcast@gmail.com</a>.</p>\n\n<p>Thanks to <a href="http://cachefly.com">Cachefly</a> for the bandwidth for this show.</p>\n\n<p><b>Running time:</b> 51:22</p>', 'language': None},
      'subtitle': u'We wear our computers, improve our toilets and all die in a singularity. But we can think our way out of it.',
      'updated_parsed': (2011, 8, 30, 19, 0, 5, 1, 242, 0),
      'links': [
        {'href': u'http://www.podtrac.com/pts/redirect.mp3/twit.cachefly.net/fc0089.mp3', 'type': 'text/html', 'rel': 'alternate'},
        {'length': u'24811632', 'href': u'http://www.podtrac.com/pts/redirect.mp3/twit.cachefly.net/fc0089.mp3', 'type': u'audio/mpeg', 'rel': 'enclosure'}],
      'title': u'FourCast 89: We Welcome Our Tank Spider Overlords',
      'itunes_explicit': None,
      'author': u'Leo Laporte (leo@leoville.com)',
      'updated': u'Tue, 30 Aug 2011 12:00:05 -0700',
      'comments': u'http://twit.tv/fc89',
      'summary': u'<p><img align="right" border="0" hspace="20" src="http://leoville.tv/podcasts/coverart/fc144.jpg" title="FourCast" vspace="20" /></p>\n\n<p><b>Hosts:</b> <a href="http://tommerritt.com">Tom Merritt</a> and <a href="http://frogpants.com/">Scott Johnson</a></p>\n\n<p>We wear our computers, improve our toilets and all die in a singularity. But we can think our way out of it.</p>\n\n<p><b>Guests:</b> <a href="http://linkedin.com/in/dorseygraphics">Steve Dorsey</a> and <a href="http://twitter.com/PDelahanty">Patrick Delahanty</a>  </p>\n\n<p>Download or subscribe to this show at <a href="http://twit.tv/fc">twit.tv/fc</a>.</p>\n\n<p>Got a prediction of your own? Guest you\'d like to see? Question for the show? Email us at <a href="mailto: fourcastpodcast@gmail.com">fourcastpodcast@gmail.com</a>.</p>\n\n<p>Thanks to <a href="http://cachefly.com">Cachefly</a> for the bandwidth for this show.</p>\n\n<p><b>Running time:</b> 51:22</p>',
      'content': [
        {'base': u'http://leoville.tv/podcasts/fc.xml',
        'type': 'text/plain',
        'value': u"Hosts: Tom Merritt and Scott Johnson\n\nWe wear our computers, improve our toilets and all die in a singularity. But we can think our way out of it.\n\nGuests: Steve Dorsey and Patrick Delahanty  \n\nDownload or subscribe to this show at twit.tv/fc.\n\nGot a prediction of your own? Guest you'd like to see? Question for the show? Email us at fourcastpodcast@gmail.com.\n\nThanks to Cachefly for the bandwidth for this show.\n\nRunning time: 51:22",
        'language': None}],
      'guidislink': False,
      'title_detail': {
        'base': u'http://leoville.tv/podcasts/fc.xml',
        'type': 'text/plain',
        'value': u'FourCast 89: We Welcome Our Tank Spider Overlords',
        'language': None},
      'link': u'http://www.podtrac.com/pts/redirect.mp3/twit.cachefly.net/fc0089.mp3',
      'itunes_duration': u'51:22',
      'authors': [{}, {}],
      'author_detail': {
        'name': u'Leo Laporte',
        'email': u'leo@leoville.com'},
      'subtitle_detail': {
        'base': u'http://leoville.tv/podcasts/fc.xml',
        'type': 'text/plain',
        'value': u'We wear our computers, improve our toilets and all die in a singularity. But we can think our way out of it.',
        'language': None},
      'id': u'http://leoville.tv/podcasts/DAB67A49-9DB9-4911-9CEA-C5C8FF61427C',
      'tags': [{'term': u'Future, Predictions', 'scheme': None, 'label': None}]}

    
    {'feed': {
  'subtitle': u'Join Scott Johnson and Tom Merritt to get short term, long term, and crazy predictions from some of the smartest people on the planet.',
  'updated_parsed': (2011, 8, 30, 18, 53, 10, 1, 242, 0),
  'links': [
    {'href': u'http://www.fourcastpodcast.com', 'type': 'text/html', 'rel': 'alternate'},
    {'href': u'http://feeds.twit.tv/fc.xml', 'type': u'application/rss+xml', 'rel': u'self'}],
  'image': {'href': u'http://leo.am/fc600audio.jpg'},
  'summary_detail': {
    'base': u'http://leoville.tv/podcasts/fc.xml',
    'type': 'text/plain',
    'value': u'Join Scott Johnson and Tom Merritt to get short term, long term, and crazy predictions from some of the smartest people on the planet. From robot overlords, to growing your own meat in a dish, you never know what predictions our guest will make and where the conversation may end up. \xa0Join us for a peak at the future.',
    'language': None},
  'ttl': u'720',
  'rights_detail': {
    'base': u'http://leoville.tv/podcasts/fc.xml',
    'type': 'text/plain',
    'value': u'This work is licensed under a Creative Commons License - Attribution-NonCommercial-ShareAlike - http://creativecommons.org/licenses/by-nc-sa/3.0/',
    'language': None},
  'summary': u'Join Scott Johnson and Tom Merritt to get short term, long term, and crazy predictions from some of the smartest people on the planet. From robot overlords, to growing your own meat in a dish, you never know what predictions our guest will make and where the conversation may end up. \xa0Join us for a peak at the future.',
  'generator': u'Feeder 2.1.8(1403); Mac OS X Version 10.5.8 (Build 9L31a) http://reinventedsoftware.com/feeder/',
  'title': u'FourCast',
  'title_detail': {{
    'base': u'http://leoville.tv/podcasts/fc.xml',
    'type': 'text/plain',
    'value': u'FourCast',
    'language': None},
  'updated': u'Tue, 30 Aug 2011 11:53:10 -0700',
  'itunes_block': 0,
  'tags': [
    {'term': u'Tom', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Merritt,', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Scott', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Johnson,', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Predictions,', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Future', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Society & Culture', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Philosophy', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Science & Medicine', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'Natural Sciences', 'scheme': 'http://www.itunes.com/', 'label': None},
    {'term': u'News & Politics', 'scheme': 'http://www.itunes.com/', 'label': None}],
  'docs': u'http://blogs.law.harvard.edu/tech/rss',
  'generator_detail': {'name': u'Feeder 2.1.8(1403); Mac OS X Version 10.5.8 (Build 9L31a) http://reinventedsoftware.com/feeder/'},
  'link': u'http://www.fourcastpodcast.com',
  'authors': [{}, {'name': u'Leo Laporte', 'email': u'leo@leoville.com'}],
  'author_detail': {'name': u'Leo Laporte', 'email': u'leo@leoville.com'},
  'publisher_detail': {'name': u'Leo Laporte', 'email': u'leo@leoville.com'},
  'publisher': u'Leo Laporte (leo@leoville.com)',
  'language': u'en',
  'rights': u'This work is licensed under a Creative Commons License - Attribution-NonCommercial-ShareAlike - http://creativecommons.org/licenses/by-nc-sa/3.0/',
  'author': u'Leo Laporte (leo@leoville.com)',
  'subtitle_detail': {
      'base': u'http://leoville.tv/podcasts/fc.xml',
      'type': 'text/plain',
      'value': u'Join Scott Johnson and Tom Merritt to get short term, long term, and crazy predictions from some of the smartest people on the planet.',
      'language': None},
  'itunes_explicit': None,
  'itunes_keywords': u'Tom Merritt, Scott Johnson, Predictions, Future'},
'status': 200,
'updated': (2011, 8, 30, 18, 50, 20, 1, 242, 0),
'version': 'rss20',
'encoding': 'utf-8',
'bozo': 0,
'headers': {
    'content-encoding': 'gzip',
    'transfer-encoding': 'chunked',
    'expires': 'Wed, 31 Aug 2011 20:38:23 GMT',
    'server': 'nginx/0.7.61',
    'last-modified': 'Tue, 30 Aug 2011 18:50:20 GMT',
    'connection': 'close',
    'cache-control': 'max-age=86400',
    'date': 'Tue, 30 Aug 2011 20:38:23 GMT',
    'content-type': 'text/xml; charset=utf-8'},
'href': u'http://leoville.tv/podcasts/fc.xml',
'namespaces': {'': u'http://www.w3.org/2005/Atom', 'itunes': u'http://www.itunes.com/dtds/podcast-1.0.dtd'},


]}

