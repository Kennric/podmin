import datetime

from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Rss201rev2Feed, Atom1Feed, Enclosure
from django.shortcuts import get_object_or_404

from django.contrib.syndication.views import Feed

from podmin.models import Podcast


class PodcastElements(object):
    """
    Add the things that make a Feed a Podcast, including
    iTunes stuff( see https://www.apple.com/itunes/podcasts/specs.html)
    These items should be common to Atom and RSS
    """

    def add_root_elements(self, handler):
        """
        Add additional elements to the podcast object, these will
        be part of the <channel> definition

        """
        super(PodcastElements, self).add_root_elements(handler)
        podcast = self.feed["podcast"]

        handler.addQuickElement(u"itunes:subtitle", self.feed["subtitle"])
        handler.addQuickElement(u"itunes:author", podcast.author)

        handler.startElement(u"itunes:owner", {})
        handler.addQuickElement(u"itunes:name", podcast.owner.get_full_name())
        handler.addQuickElement(u"itunes:email", podcast.owner.email)
        handler.endElement(u"itunes:owner")

        if podcast.itunes_image:
            handler.addQuickElement(u"itunes:image",
                attrs={"href": podcast.itunes_image})


        # iTunes categories are, annoyingly, a tree. Children must be nested in
        # parent tags, but not all categories have parents or children.
        # Parents may not appear without children.
        if podcast.itunes_categories:
            for category in podcast.itunes_categories.all():
                if category.parent:
                    handler.startElement(u"itunes:category",
                        {'text': category.parent.name})
                    handler.addQuickElement(u"itunes:category",
                        attrs={'text': category.name})
                    handler.endElement(u"itunes:category")
                else:
                    handler.addQuickElement(u"itunes:category",
                        attrs={'text': category.name})

        handler.addQuickElement(u"itunes:summary", podcast.description)
        handler.addQuickElement(u"itunes:explicit",
                                podcast.get_explicit_display())
        if podcast.redirect:
            handler.addQuickElement(u"itunes:new-feed-url", podcast.redirect)

        if podcast.editor_email:
            handler.addQuickElement(u"managingEditor", podcast.editor_email)

        if podcast.webmaster_email:
            handler.addQuickElement(u"webMaster", podcast.webmaster_email)

        handler.addQuickElement(u"generator", podcast.generator)

    def add_item_elements(self, handler, item):
        """
        Add additional elements to the episode object, these will be part
        of each <item>

        """
        super(PodcastElements, self).add_item_elements(handler, item)
        episode = item["episode"]

        """
        handler.addQuickElement(
            u"copyright", "{0} {1} {2}".format(
                episode.podcast.copyright,
                episode.podcast.copyright_url,
                datetime.date.today().year))
        """

        handler.addQuickElement(u"itunes:author", episode.podcast.author)
        handler.addQuickElement(u"itunes:subtitle", episode.subtitle)
        handler.addQuickElement(u"itunes:summary", episode.description)
        handler.addQuickElement(u"itunes:duration", episode.length)
        handler.addQuickElement(u"itunes:keywords", episode.tags)
        handler.addQuickElement(u"itunes:explicit", episode.podcast.explicit)
        if episode.block:
            handler.addQuickElement(u"itunes:block", "yes")
        if episode.image:
            handler.addQuickElement(u"itunes:image",
                                    attrs={"href": episode.image.url})

    def namespace_attributes(self):
        return {u"xmlns:itunes": u"http://www.itunes.com/dtds/podcast-1.0.dtd"}


class AtomElements(PodcastElements):
    """
    Add podcast elements here that are specific to Atom feeds
    """

    def add_root_elements(self, handler):
        super(AtomElements, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        super(AtomElements, self).add_item_elements(handler, item)


class RSSElements(PodcastElements):
    """
    Add podcast elements here that are specific to RSS feeds
    """

    def add_root_elements(self, handler):
        super(RSSElements, self).add_root_elements(handler)
        if self.feed["podcast"].rss_image:
            handler.startElement(u"image", {})
            handler.addQuickElement(u"url", self.feed["podcast"].rss_image)
            handler.addQuickElement(u"title", self.feed["title"])
            handler.addQuickElement(u"link", self.feed["link"])
            handler.endElement(u"image")

    def add_item_elements(self, handler, item):
        super(RSSElements, self).add_item_elements(handler, item)
        handler.addQuickElement(u"guid", str(item['episode'].guid),
                                attrs={"isPermaLink": "false"})


class AtomPodcastFeedGenerator(AtomElements, Atom1Feed):

    def root_attributes(self):
        atom_attrs = super(AtomPodcastFeedGenerator, self).root_attributes()
        atom_attrs.update(self.namespace_attributes())
        return atom_attrs


class RssPodcastFeedGenerator(RSSElements, Rss201rev2Feed):

    def rss_attributes(self):
        rss_attrs = super(RssPodcastFeedGenerator, self).rss_attributes()
        rss_attrs.update(self.namespace_attributes())
        return rss_attrs


class PodcastFeed(Feed):

    """
    A feed of iTunes compatible podcasts
    """

    def title(self, podcast):
        return podcast.title

    def feed_copyright(self, podcast):
        return "{0} {1} {2}".format(podcast.copyright, podcast.copyright_url,
                                    datetime.date.today().year)

    def ttl(self, podcast):
        return podcast.ttl

    def items(self, podcast):
        return podcast.episode_set.filter(pub_date__lte=datetime.datetime.now(),
                                          active=True)

    def get_object(self, request, *args, **kwargs):
        self.podcast = get_object_or_404(Podcast, slug=kwargs["podcast_slug"])
        return self.podcast

    def item_title(self, episode):
        return episode.title

    def item_description(self, episode):
        "renders summary for atom"
        return episode.description

    def item_link(self, episode):
        #return "http://fuck.you.com"
        return reverse("episode_show",
                       kwargs={"slug": episode.podcast.slug,
                               "eid": episode.id})

    # def item_author_link(self, episode):
    #     return "todo" #this one doesn't add anything in atom or rss
    #
    # def item_author_email(self, episode):
    #     return "todo" #this one doesn't add anything in atom or rss

    def item_pubdate(self, episode):
        return episode.published

    def item_updateddate(self, episode):
        return episode.updated

    def item_enclosure_url(self, episode):
        try:
            return episode.audio_url
        except Enclosure.DoesNotExist:
            pass

    def item_enclosure_length(self, episode):
        try:
            e = episode.size
            return e
        except Enclosure.DoesNotExist:
            pass

    def item_enclosure_mime_type(self, episode):
        try:
            e = episode.mime_type
            return e
        except Enclosure.DoesNotExist:
            pass

    def item_keywords(self, episode):
        return episode.tags

    def feed_extra_kwargs(self, obj):
        extra = {}
        extra["podcast"] = self.podcast
        return extra

    def item_extra_kwargs(self, item):
        extra = {}
        extra["episode"] = item
        return extra


class AtomPodcastFeed(PodcastFeed):
    feed_type = AtomPodcastFeedGenerator

    def subtitle(self, podcast):
        return podcast.subtitle

    def author_name(self, podcast):
        return podcast.owner.get_full_name()

    def author_email(self, podcast):
        return podcast.owner.email

    def author_link(self, podcast):
        return podcast.contact

    def link(self, podcast):
        return "%s/%s" % (podcast.pub_url, "atom.xml-feed_link_atom")

    def feed_url(self, podcast):
        return "%s/%s" % (podcast.pub_url, "atom.xml-feed_url_atom")

class RssPodcastFeed(PodcastFeed):
    feed_type = RssPodcastFeedGenerator

    def item_guid(self, episode):
        # ITunesElements can't add isPermaLink attr unless None is
        # returned here."
        return None

    def description(self, podcast):
        return podcast.description

    def subtitle(self, podcast):
        return podcast.subtitle

    def link(self, podcast):
        return "%s/%s" % (podcast.pub_url, "rss.xml-feed_link_rss")

    def feed_url(self, podcast):
        return "%s/%s" % (podcast.pub_url, "rss.xml-feed_url_rss")