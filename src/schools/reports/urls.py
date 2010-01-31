from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
urlpatterns = patterns('schools.reports.views',
    url(r'invoice/$', 'invoice', name='invoice'),
    url(r'invoice/pdf/$', 'invoice_pdf', name='invoice_pdf'),
    url(r'lesson-analysis/$', 'lesson_analysis', name='lesson-analysis'),
    url(r'course-plan/$', 'course_plan', name='course-plan'),
    url(r'company-added-value/$', 'company_added_value', name='company-added-value'),
    url(r'$', direct_to_template, {'template':'reports/base.html'}, name='reports'),
)