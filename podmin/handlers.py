# django stuff
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# podmin app stuff
from models import Podcast, Episode
from util import podcast_audio, image_sizer

# util stuff
from shutil import rmtree
from os import path

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

    """ Danger! don't delete things we didn't create!

    media_dir = kwargs['instance'].storage_dir
    buffer_dir = kwargs['instance'].buffer_dir
    pub_dir = kwargs['instance'].pub_dir

    if path.isdir(media_dir):
        rmtree(media_dir)

    if path.isdir(buffer_dir):
        rmtree(buffer_dir)

    if path.isdir(pub_dir):
        rmtree(pub_dir)

    """


# signal catcher, post delete for episode:
@receiver(post_delete, sender=Episode)
def episode_post_delete(sender, **kwargs):

    if path.isfile():
        rmtree(media_dir)

    if path.isdir(buffer_dir):
        rmtree(buffer_dir)


post_save.connect(podcast_post_save, sender=Podcast)
post_delete.connect(podcast_post_delete, sender=Podcast)
