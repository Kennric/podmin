from django.conf.urls import patterns, url, include
from django.contrib import admin


urlpatterns = patterns('',
    #url(
    #r'^accounts/login/$', 'django.contrib.auth.views.login',
    #{'template_name': 'podmin/login.html'}),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('', url(r'', include('podmin.urls_feeds')))


urlpatterns += patterns(
    'podmin.views',

    url(r'^login/?$', 'login_user', name='login'),
    url(r'^logout/?$', 'logout_user', name='logout'),
    url(r'^$', 'index', name='index'),
    url(r'^about/$',
        'podmin_info', name='about'),
    url(r'^home/$',
        'home', name='user_home'),
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
)
