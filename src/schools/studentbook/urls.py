from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('schools.studentbook.views',
        url(r'$', 'studentbook',name='studentbook'),
)