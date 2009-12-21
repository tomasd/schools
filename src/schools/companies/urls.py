from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object
from schools.companies.models import Company
from schools.search.views import object_list
from generic_views.views.delete import delete_object

urlpatterns = patterns('schools.companies.views',
    url(r'company/create/$', create_object, {'model':Company}, name='companies_company_create'),
    url(r'company/(?P<object_id>\d+)/$', 'company_update', {'model':Company}, name='companies_company_update'),
    url(r'company/(?P<object_id>\d+)/students/$', 'company_students', name='companies_company_students'),
    url(r'company/(?P<object_id>\d+)/delete/$', delete_object, {'model':Company, 'post_delete_redirect':'companies_company_list'}, name='companies_company_delete'),
    url(r'company/$', object_list, {'queryset':Company.objects.all(), 'search_fields':['name__contains']}, name='companies_company_list'),
)