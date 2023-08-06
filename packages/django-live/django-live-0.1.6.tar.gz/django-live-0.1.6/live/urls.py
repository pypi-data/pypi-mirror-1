from django.conf.urls.defaults import *

urlpatterns = patterns('live.views',
    (r'^$', 'index'),
    (r'^chat/$', 'chat'),
    (r'^chat/(?P<channel>[\d\.]+)/$', 'chat'),
    (r'^chat/(?P<channel>[\d\.]+)/(?P<username>\w+)$', 'chat'),
    (r'^manage/$', 'manage'),
    (r'^public/(?P<room>\w+)$', 'public'),
    (r'^public/$', 'public'),
)
