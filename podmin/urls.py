from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.conf import settings
import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'podmin/login.html'}),
)

urlpatterns += patterns('podmin.views',    
    url(r'^$', 'index', name='index'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)podcasts/$', 'podcasts', name='podcasts_list'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)podcast/(?P<slug>[A-Za-z0-9\-]+)/$', 'podcast', name='podcast_show'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)podcast/edit/(?P<slug>[A-Za-z0-9\-]+)/$','edit_podcast', name='podcast_edit'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)podcast/new/$', 'new_podcast', name='podcast_new'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/(?P<eid>\d+)/$', 'episode', name='episode_show'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/edit/(?P<eid>\d+)/$', 'edit_episode', name='episode_edit'),
    url(r'^(?P<subsite>[A-Za-z0-9/]*)episode/new/(?P<pid>\d+)/$', 'new_episode', name='episode_new'),
    url(r'^(?P<subsite>\w+)/$', 'index', name='index'),

    #(?:/(?P<title>[a-zA-Z]+))?/$
    #url(r'^my/$', 'control'),
    #url(r'^podcast/(\d{1,8})/$', 'edit_podcast'),
    #url(r'^episode/(\d{1,8})/$', 'edit_podcast'),
)

urlpatterns += patterns('', 
    url(r'', include('podmin.urls_feeds'))
)
# for handling user-uploaded podcast logo in the future
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)