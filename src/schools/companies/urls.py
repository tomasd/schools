from django.conf.urls.defaults import patterns, url
from schools.companies.models import Company

urlpatterns = patterns('schools.companies.views',
    url(r'company/create/$', 'company_create', {'model':Company}, name='companies_company_create'),
    url(r'company/(?P<object_id>\d+)/$', 'company_update', {'model':Company}, name='companies_company_update'),
    url(r'company/(?P<object_id>\d+)/students/$', 'company_students', name='companies_company_students'),
    url(r'company/(?P<object_id>\d+)/delete/$', 'company_delete', {'model':Company, 'post_delete_redirect':'companies_company_list'}, name='companies_company_delete'),
    url(r'company/(?P<object_id>\d+)/users/$', 'company_users', name='companies_company_users'),
    url(r'company/(?P<object_id>\d+)/users/create/$', 'company_user_create', name='companies_company_user_create'),
    url(r'company/(?P<company_id>\d+)/users/(?P<object_id>\d+)$', 'company_user_update', name='companies_company_user_update'),
    url(r'company/$', 'company_list', {'queryset':Company.objects.all(), 'search_fields':['name__contains']}, name='companies_company_list'),
)