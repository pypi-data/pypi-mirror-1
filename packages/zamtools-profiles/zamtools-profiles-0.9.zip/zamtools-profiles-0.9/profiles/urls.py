from django.conf.urls.defaults import *
from models import Member

urlpatterns = patterns('profiles.views', 
    url(r'^$', 'index', {}, name='profile_index'),
)