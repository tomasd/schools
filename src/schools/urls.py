from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

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
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT})
)