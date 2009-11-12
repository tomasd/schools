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
    url(r'^$', direct_to_template, {'template':'base.html'}),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT})
)