from django.conf.urls.defaults import *

urlpatterns = patterns('profiles.views',
    url(r'^profiles/$', 'index', {}, name='profiles_index'),
)