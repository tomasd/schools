from django.conf.urls.defaults import patterns, url
from schools.companies.models import Company

urlpatterns = patterns('schools.companies.views',
    url(r'company/create/$', 'company_create', {'model':Company}, name='companies_company_create'),
    url(r'company/(?P<object_id>\d+)/$', 'company_update', {'model':Company}, name='companies_company_update'),
    url(r'company/(?P<object_id>\d+)/students/$', 'company_students', name='companies_company_students'),
    url(r'company/(?P<object_id>\d+)/delete/$', 'company_delete', {'model':Company, 'post_delete_redirect':'companies_company_list'}, name='companies_company_delete'),
    url(r'company/$', 'company_list', {'queryset':Company.objects.all(), 'search_fields':['name__contains']}, name='companies_company_list'),
)