from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('schools.companybook.views',
        url(r'students/$', 'company_students',name='companybook_students'),
        url(r'$', 'companybook',name='companybook'),
)