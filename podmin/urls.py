from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings
import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'podmin/login.html'}),
    url(r'^$', 'podmin.views.index', name='index'),
    url(r'^podcasts/$', 'podmin.views.podcasts'),
    url(r'^podcast/(?P<pid>\d+)/$', views.podcast, name='podcast'),
    url(r'^podcast(?:/edit/(?P<pid>\d+))?/$',
        views.edit_podcast,
        name='edit_podcast'),
    url(r'^podcast/new/$', views.new_podcast, name='new_podcast'),
    url(r'^episode/(?P<eid>\d+)/$', views.episode, name='episode'),
    url(r'^episode/edit/(?P<eid>\d+)/$',
        views.edit_episode,
        name='edit_episode'),
    url(r'^episode/new/(?P<pid>\d+)/$',
        views.new_episode,
        name='new_episode'),
    #(?:/(?P<title>[a-zA-Z]+))?/$
    #url(r'^my/$', 'podmin.views.control'),
    #url(r'^podcast/(\d{1,8})/$', 'podmin.views.edit_podcast'),
    #url(r'^episode/(\d{1,8})/$', 'podmin.views.edit_podcast'),

)
# for handling user-uploaded podcast logo in the future
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
