from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Set up the admin group and permissions.'

    def handle(self, *args, **options):
        user_ctype = ContentType.objects.get(app_label='auth', model='user')
        podcast_ctype = ContentType.objects.get(app_label='podmin',
                                                model='podcast')
        perms = {'Can add podcast': podcast_ctype,
                 'Can change podcast': podcast_ctype,
                 'Can change podcast': podcast_ctype,
                 'Can add user': user_ctype,
                 'Can change user': user_ctype,
                 'Can change user': user_ctype}

        group, created = Group.objects.get_or_create(name='admins')

        for perm, ctype in perms.iteritems():
            p, created = Permission.objects.get_or_create(
                codename=perm.replace(' ', '_'),
                name=perm,
                content_type=ctype)
            p.save()

            group.permissions.add(p)
            group.save()
