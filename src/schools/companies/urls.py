from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object, update_object
from schools.companies.models import Company
from django.views.generic.list_detail import object_list

urlpatterns = patterns('',
    url(r'company/create/$', create_object, {'model':Company}, name='companies_company_create'),
    url(r'company/(?P<object_id>\d+)/$', update_object, {'model':Company}, name='companies_company_update'),
    url(r'company/$', object_list, {'queryset':Company.objects.all()}, name='companies_company_list'),
)