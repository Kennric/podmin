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
    url(r'^podcasts/$', 'podcasts'),
    url(r'^podcast/(?P<pid>\d+)/$', 'podcast', name='podcast'),
    url(r'^podcast(?:/edit/(?P<pid>\d+))?/$','edit_podcast', name='edit_podcast'),
    url(r'^podcast/new/$', 'new_podcast', name='new_podcast'),
    url(r'^episode/(?P<eid>\d+)/$', 'episode', name='episode'),
    url(r'^episode/edit/(?P<eid>\d+)/$',
        'edit_episode',
        name='edit_episode'),
    url(r'^episode/new/(?P<pid>\d+)/$',
        'new_episode',
        name='new_episode'),
    
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