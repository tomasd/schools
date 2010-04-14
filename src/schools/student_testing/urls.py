from django.conf.urls.defaults import *
from schools.student_testing.models import TestingTerm

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('schools.student_testing.views',
    url('testing-term/(?P<object_id>\d+)/delete/$', 'delete_testing_term', {'model':TestingTerm}, 'testing_term_delete'),
)