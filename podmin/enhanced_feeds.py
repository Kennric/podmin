from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.feedgenerator import SyndicationFeed, rfc2822_date


class CDataXMLGenerator(SimplerXMLGenerator):
    def characters(self, contents):
        # check the given string for CDATA and if it's present,
        # call parent.characters() for the non-CDATA parts
        # and parent._write() for the CDATA
        start = 0
        cdata_start = '<![CDATA['
        cdata_end = ']]>'
        while True:
            try:
                idx = contents.index(cdata_start, start)
                end = contents.index(cdata_end, start) + len(cdata_end)
                if start < idx:
                    SimplerXMLGenerator.characters(self, (contents[start:idx]))
                # now write out the stuff, and reset start:
                # this sax stuff uses old-school python classes
                # so no using super()
                SimplerXMLGenerator._write(self, contents[idx:end])
                start = end
            except ValueError:
                SimplerXMLGenerator.characters(self, contents[start:])
                break


class EnhancedPodcastFeed(SyndicationFeed):
    """
    This provides a feed in which CDATA elements can appear with their
    contents unescaped. Using CDataXMLGenerator, whenever a CDATA tag
    is found in the contents of a tag, it is left intact and the contents
    left unescaped
    """
    mime_type = 'application/rss+xml; charset=utf-8'

    def write(self, outfile, encoding):
        handler = CDataXMLGenerator(outfile, encoding)
        handler.startDocument()
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement("rss")

    def rss_attributes(self):
        return {"version": self._version,
                "xmlns:atom": "http://www.w3.org/2005/Atom"}

    def write_items(self, handler):
        for item in self.items:
            handler.startElement('item', self.item_attributes(item))
            self.add_item_elements(handler, item)
            handler.endElement("item")

    def add_root_elements(self, handler):
        handler.addQuickElement("title", self.feed['title'])
        handler.addQuickElement("link", self.feed['link'])
        handler.addQuickElement("description", self.feed['description'])
        if self.feed['feed_url'] is not None:
            handler.addQuickElement("atom:link", None,
                                    {"rel": "self",
                                     "href": self.feed['feed_url']})
        if self.feed['language'] is not None:
            handler.addQuickElement("language", self.feed['language'])
        for cat in self.feed['categories']:
            handler.addQuickElement("category", cat)
        if self.feed['feed_copyright'] is not None:
            handler.addQuickElement("copyright", self.feed['feed_copyright'])

        handler.addQuickElement("lastBuildDate",
                                rfc2822_date(self.latest_post_date()))
        if self.feed['ttl'] is not None:
            handler.addQuickElement("ttl", self.feed['ttl'])

    def endChannelElement(self, handler):
        handler.endElement("channel")


class EnhancedRss201rev2Feed(EnhancedPodcastFeed):
    # Spec: http://blogs.law.harvard.edu/tech/rss
    _version = "2.0"

    def add_item_elements(self, handler, item):
        handler.addQuickElement("title", item['title'])
        handler.addQuickElement("link", item['link'])
        if item['description'] is not None:
            handler.addQuickElement("description", item['description'])

        # Author information.
        if item["author_name"] and item["author_email"]:
            handler.addQuickElement("author", "%s (%s)" %
                                    (item['author_email'],
                                     item['author_name']))
        elif item["author_email"]:
            handler.addQuickElement("author", item["author_email"])
        elif item["author_name"]:
            handler.addQuickElement("dc:creator", item["author_name"],
                {"xmlns:dc": "http://purl.org/dc/elements/1.1/"})

        if item['pubdate'] is not None:
            handler.addQuickElement("pubDate", rfc2822_date(item['pubdate']))
        if item['comments'] is not None:
            handler.addQuickElement("comments", item['comments'])
        if item['unique_id'] is not None:
            guid_attrs = {}
            if isinstance(item.get('unique_id_is_permalink'), bool):
                guid_attrs['isPermaLink'] = str(
                    item['unique_id_is_permalink']).lower()
            handler.addQuickElement("guid", item['unique_id'], guid_attrs)
        if item['ttl'] is not None:
            handler.addQuickElement("ttl", item['ttl'])

        # Enclosure.
        if item['enclosure'] is not None:
            handler.addQuickElement("enclosure", '',
                                    {"url": item['enclosure'].url,
                                     "length": item['enclosure'].length,
                                     "type": item['enclosure'].mime_type})

        # Categories.
        for cat in item['categories']:
            handler.addQuickElement("category", cat)
