import datetime

from django.core.urlresolvers import reverse
from django.utils.feedgenerator import rfc2822_date, Rss201rev2Feed, Atom1Feed
from django.shortcuts import get_object_or_404

from django.contrib.syndication.views import Feed

from podmin.models import Podcast, Episode


class ITunesElements(object):

    def add_root_elements(self, handler):
        """ Add additional elements to the podcast object"""
        super(ITunesElements, self).add_root_elements(handler)
        podcast = self.feed["podcast"]
        handler.addQuickElement(u"guid", str(podcast.slug),
                                attrs={"isPermaLink": "false"})
        handler.addQuickElement(u"itunes:subtitle", self.feed["subtitle"])
        handler.addQuickElement(u"itunes:author", podcast.author)
        handler.startElement(u"itunes:owner", {})
        handler.addQuickElement(u"itunes:name", podcast.owner.get_full_name())
        handler.addQuickElement(u"itunes:email", podcast.owner.email)
        handler.endElement(u"itunes:owner")

        # handler.addQuickElement(u"itunes:image",
        #                        attrs={"href": podcast.image.url})

        #handler.startElement(u"image", {})
        #handler.addQuickElement(u"url", podcast.image.url)
        #handler.addQuickElement(u"title", self.feed["title"])
        #handler.addQuickElement(u"link", self.feed["link"])
        #handler.endElement(u"image")

        handler.addQuickElement(u"itunes:category", podcast.itunes_categories)
        handler.addQuickElement(u"itunes:summary", podcast.description)
        handler.addQuickElement(u"itunes:explicit",
                                podcast.get_explicit_display())
        if podcast.redirect:
            handler.addQuickElement(u"itunes:new-feed-url", podcast.redirect)
        handler.addQuickElement(u"keywords", podcast.keywords)
        if podcast.editor_email:
            handler.addQuickElement(u"managingEditor", podcast.editor_email)
        if podcast.webmaster_email:
            handler.addQuickElement(u"webMaster", podcast.webmaster_email)

        handler.addQuickElement(u"generator", podcast.generator)


    def add_item_elements(self, handler, item):
        """ Add additional elements to the episode object"""
        super(ITunesElements, self).add_item_elements(handler, item)
        episode = item["episode"]
        handler.addQuickElement(u"guid", str(episode.guid),
                                attrs={"isPermaLink": "false"})
        handler.addQuickElement(u"copyright",
            "{0} {1} {2}".format(episode.podcast.copyright,
            episode.podcast.copyright_url,
            datetime.date.today().year))
        handler.addQuickElement(u"itunes:author", episode.podcast.author)
        handler.addQuickElement(u"itunes:subtitle", episode.subtitle)
        handler.addQuickElement(u"itunes:summary", episode.description)
        handler.addQuickElement(u"itunes:duration", episode.length)
        handler.addQuickElement(u"itunes:keywords", episode.tags)
        handler.addQuickElement(u"itunes:explicit", episode.podcast.explicit)
        if episode.block:
            handler.addQuickElement(u"itunes:block", "yes")
        #handler.addQuickElement(u"itunes:image",
        #                        attrs={"href": episode.image.url})
        #handler.startElement(u"image", {})
        #handler.addQuickElement(u"url", episode.image.url)
        #handler.addQuickElement(u"title", episode.title)
        #handler.addQuickElement(u"link", episode.get_absolute_url())
        #handler.endElement(u"image")

    def namespace_attributes(self):
        return {u"xmlns:itunes": u"http://www.itunes.com/dtds/podcast-1.0.dtd"}


class AtomITunesFeedGenerator(ITunesElements, Atom1Feed):
    def root_attributes(self):
        atom_attrs = super(AtomITunesFeedGenerator, self).root_attributes()
        atom_attrs.update(self.namespace_attributes())
        return atom_attrs


class RssITunesFeedGenerator(ITunesElements, Rss201rev2Feed):
    def rss_attributes(self):
        rss_attrs = super(RssITunesFeedGenerator, self).rss_attributes()
        rss_attrs.update(self.namespace_attributes())
        return rss_attrs


class PodcastFeed(Feed):
    """
    A feed of podcasts for iTunes and other compatible podcatchers.
    """
    def title(self, podcast):
        return podcast.title

    def link(self, podcast):
        return podcast.website

    def feed_copyright(self, podcast):
        return "{0} {1} {2}".format(podcast.copyright, podcast.copyright_url,
                                    datetime.date.today().year)

    def ttl(self, podcast):
        return podcast.ttl

    def items(self, podcast):
        return podcast.episode_set.all()

    def get_object(self, request, *args, **kwargs):
        self.podcast = get_object_or_404(Podcast, slug=kwargs["podcast_slug"])
        return self.podcast

    def item_title(self, episode):
        return episode.title

    def item_description(self, episode):
        "renders summary for atom"
        return episode.description

    def item_link(self, episode):
        return reverse("episode", kwargs={"eid": episode.id})

    # def item_author_link(self, episode):
    #     return "todo" #this one doesn't add anything in atom or rss
    #
    # def item_author_email(self, episode):
    #     return "todo" #this one doesn't add anything in atom or rss

    def item_pubdate(self, episode):
        return episode.published


    def item_enclosure_url(self, episode):
        try:
            e = episode.enclosure_file
            return e.url
        except Enclosure.DoesNotExist:
            pass

    def item_enclosure_length(self, episode):
        try:
            e = episode.size
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
    feed_type = AtomITunesFeedGenerator

    def subtitle(self, podcast):
        return podcast.subtitle

    def author_name(self, podcast):
        return podcast.owner.get_full_name()

    def author_email(self, podcast):
        return podcast.owner.email

    def author_link(self, podcast):
        return podcast.contact


class RssPodcastFeed(PodcastFeed):
    feed_type = RssITunesFeedGenerator

    def item_guid(self, episode):
        "ITunesElements can't add isPermaLink attr unless None is returned here."
        return None

    def description(self, podcast):
        return podcast.description
