from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^skoly/', include('skoly.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^buildings/', include('schools.buildings.urls')),
    url(r'^companies/', include('schools.companies.urls')),
    url(r'^lectors/', include('schools.lectors.urls')),
    url(r'^students/', include('schools.students.urls')),
    url(r'^courses/', include('schools.courses.urls')),
    url(r'^reports/', include('schools.reports.urls')),
    url(r'^studentbook/', include('schools.studentbook.urls')),
    url(r'^companybook/', include('schools.companybook.urls')),
    url(r'^$', direct_to_template, {'template':'home.html'}, name='home'),
)

# user management
urlpatterns += patterns('', 
    url('^change-password/$', 'django.contrib.auth.views.password_change', name='password-change'),
    url('^change-password/done/$', 'django.contrib.auth.views.password_change_done', name='password-change-done'),
    url('^login/$', 'django.contrib.auth.views.login', name='login'),
    url('^logout/$', 'django.contrib.auth.views.logout', name='logout'),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT})
)