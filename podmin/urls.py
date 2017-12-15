from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^markdown/', include('django_markdown.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}))

urlpatterns += patterns('', url(r'', include('podmin.urls_feeds')))

urlpatterns += patterns(
    'podmin.views',
    url(r'^login/?$', 'login_user', name='login'),
    url(r'^logout/?$', 'logout_user', name='logout'),
    url(r'^request/?$', 'podcast_request', name='podcast_request'),
    url(r'^podcasts/$', 'podcasts', name='podcasts'),
    url(r'^$', 'index', name='home'),
    url(r'^about/$',
        'podmin_info', name='about'),
    url(r'^home/$',
        'user_home', name='user_home'),
    url(r'^podcasts/$',
        'podcasts', name='podcasts_list'),
    url(r'^new/$',
        'new_podcast', name='podcast_new'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/$',
        'podcast', name='podcast_show'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/edit/$',
        'edit_podcast', name='podcast_edit'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/delete/$',
        'delete_podcast', name='podcast_delete'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/new/$',
        'new_episode', name='episode_new'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/$',
        'episode', name='episode_show'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/edit/$',
        'edit_episode', name='episode_edit'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/delete/$',
        'delete_episode', name='episode_delete'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/depublish/$',
        'depublish_episode', name='episode_depublish'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/publish/$',
        'publish_episode', name='episode_publish'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/mothball/$',
        'mothball_episode', name='episode_mothball'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/audio_buffer/$',
        'audio_buffer', name='audio_buffer'),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/(?P<eid>\d+)/image_buffer/(?P<size>[A-Za-z0-9\-]+)$',  # noqa
        'image_buffer', name='image_buffer'),
)
