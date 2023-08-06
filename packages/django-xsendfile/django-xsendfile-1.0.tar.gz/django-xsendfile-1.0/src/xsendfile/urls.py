from django.conf.urls.defaults import *
from views import get_file

urlpatterns = patterns('',
    url(r'^get/(?P<file_id>\d+)/$', get_file, name='xsendfile_get'),
)
