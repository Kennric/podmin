# django stuff
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# podmin app stuff
from models import Podcast, Episode
from util import image_sizer

# python stuff
from shutil import rmtree
from os import path, remove
import glob


# signal catcher, post save for podcast, create groups with
# permissions as defined in GROUP_PERMS
@receiver(post_save, sender=Podcast)
def podcast_post_save(sender, **kwargs):

    if kwargs['created']:
        slug = kwargs['instance'].slug
        content_type = ContentType.objects.get(app_label='podmin',
                                               model='podcast')

        for group, perm in kwargs['instance'].GROUP_PERMS.iteritems():
            p, created = Permission.objects.get_or_create(
                codename='%s_%s' % (slug, perm),
                name='Can %s podcast %s' % (perm, slug),
                content_type=content_type)
            p.save()

            g, created = Group.objects.get_or_create(
                name='%s_%s' % (slug, group))
            g.permissions.add(p)
            g.save()

    # now resize the podcast cover art for web, itunes and rss
    if path.isfile(kwargs['instance'].image.path):
        image_sizer.make_image_sizes(kwargs['instance'].image.path)

# signal catcher, post delete for podcast:
# delete all the associated groups and perms
@receiver(post_delete, sender=Podcast)
def podcast_post_delete(sender, **kwargs):
    slug = kwargs['instance'].slug
    content_type = ContentType.objects.get(app_label='podmin',
                                           model='podcast')
    for group, perm in kwargs['instance'].GROUP_PERMS.iteritems():
        g = Group.objects.get(name='%s_%s' % (slug, group))
        g.permissions.clear()
        g.delete()

        p = Permission.objects.get(
            codename='%s_%s' % (slug, perm),
            name='Can %s podcast %s' % (perm, slug),
            content_type=content_type)
        p.delete()

    # Danger! don't delete things we didn't create!

    media_dir = path.join(settings.MEDIA_ROOT, kwargs['instance'].slug)

    buffer_dir = path.join(settings.BUFFER_ROOT, kwargs['instance'].slug)

    try:
        rmtree(media_dir)
    except IOError as err:
        # TODO handle this
        print(err)
    try:
        rmtree(buffer_dir)
    except IOError as err:
        # TODO handle this
        print(err)


# signal catcher, post delete for episode:
@receiver(post_delete, sender=Episode)
def episode_post_delete(sender, **kwargs):
    pub_image_path = path.join(
        settings.MEDIA_ROOT,
        kwargs['instance'].podcast.slug, "img")

    buffer_image_path = path.join(
        settings.BUFFER_ROOT,
        kwargs['instance'].podcast.slug, "img")

    buffer_image_name, ext = path.splitext(path.basename(
        kwargs['instance'].buffer_image.name))

    pub_image_name, ext = path.splitext(path.basename(
        kwargs['instance'].image.name))

    try:
        remove(kwargs['instance'].buffer_audio.path)
    except:
        # TODO handle this
        pass

    try:
        remove(kwargs['instance'].audio.path)
    except:
        # TODO handle this
        pass

    try:
        image_glob = "{0}/{1}*{2}".format(buffer_image_path,
                                          buffer_image_name, ext)
        for image in glob.iglob(image_glob):
            remove(image)
    except:
        # TODO handle this
        pass

    try:
        image_glob = "{0}/{1}*{2}".format(pub_image_path,
                                          pub_image_name, ext)
        for image in glob.iglob(image_glob):
            remove(image)
    except:
        # TODO handle this
        pass


post_save.connect(podcast_post_save, sender=Podcast)
post_delete.connect(podcast_post_delete, sender=Podcast)
post_delete.connect(episode_post_delete, sender=Episode)
