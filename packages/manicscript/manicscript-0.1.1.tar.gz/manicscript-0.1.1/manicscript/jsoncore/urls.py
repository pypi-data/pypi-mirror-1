from django.conf.urls.defaults import *

urlpatterns = patterns('manicscript.jsoncore.json',
    # Account operations
    (r'^profile/$', 'profile'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
)
