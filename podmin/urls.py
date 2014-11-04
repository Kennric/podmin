from django.conf.urls import patterns, url, include
#from django.conf.urls.static import static
#from django.conf import settings
#import views


"""
The web server gives us a slug to load up if we are called as a virtual
domain. i.e. mysite.com/podcasts should result in the podcast/mysite view
"""

try:
    virtual_slug = os.environ['PODMIN_SLUG']
except:
    virtual_slug = False


urlpatterns = patterns('', url(
    r'^login/$', 'django.contrib.auth.views.login',
    {'template_name': 'podmin/login.html'}),
)

urlpatterns += patterns('', url(r'', include('podmin.urls_feeds')))

"""
if virtual_slug:
    urlpatterns += patterns(
        'podmin.views',
        url(r'^(?P<subsite>[A-Za-z0-9/]*)/$',
            'podcast', {'slug': virtual_slug}, name='podcast_show'),
        url(r'^(?P<subsite>[A-Za-z0-9/]*)edit/$',
            'edit_podcast',  {'slug': virtual_slug}, name='podcast_edit'),
        url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/(?P<eid>\d+)/$',
            'episode', name='episode_show'),
        url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/edit/(?P<eid>\d+)/$',
            'edit_episode', name='episode_edit'),
        url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/new/(?P<pid>\d+)/$',
            'new_episode',  {'slug': virtual_slug}, name='episode_new'),
        url(r'^(?P<subsite>\w+)/$', 'index', name='index'),
    )

else:
"""
urlpatterns += patterns(
    'podmin.views',
    url(r'^$', 'index', name='index'),
    url(r'^podcasts/$',
        'podcasts', name='podcasts_list'),
    url(r'^podcast/(?P<slug>[A-Za-z0-9\-]+)/$',
        'podcast', name='podcast_show'),
    url(r'^podcast/edit/(?P<slug>[A-Za-z0-9\-]+)/$',
        'edit_podcast', name='podcast_edit'),
    url(r'^podcast/new/$',
        'new_podcast', name='podcast_new'),
    url(r'^episode/(?P<eid>\d+)/$',
        'episode', name='episode_show'),
    url(r'^episode/edit/(?P<eid>\d+)/$',
        'edit_episode', name='episode_edit'),
    url(r'^episode/new/(?P<pid>\d+)/$',
        'new_episode', name='episode_new'),

    #(?:/(?P<title>[a-zA-Z]+))?/$
)


# for handling user-uploaded podcast logo in the future
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
