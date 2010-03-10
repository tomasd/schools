from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('schools.studentbook.views',
        url(r'detail/$', 'studentbook',name='studentbook'),
        url(r'lector/(?P<object_id>\d+)/$', 'lector',name='studentbook_lector'),
)