from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag('listtable.html')
def listtable(object_list, column_name):
    return {'object_list': object_list, 'main_column':column_name, 'MEDIA_URL':settings.MEDIA_URL}