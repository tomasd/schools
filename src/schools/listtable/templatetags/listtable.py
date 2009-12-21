from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
import re
register = template.Library()

@register.inclusion_tag('listtable.html', takes_context=True)
def listtable(context, object_list, column_name):
    d = {'main_column':column_name}
    context.update(d)
    return context

@register.tag
def listtable_columns(parser, token):
    values = token.split_contents()
    object_list = values[1]
    values = values[2:]
    
    # tuples are in form of value as column_name
    field_values = [a for i, a in enumerate( values) if i%3==0 ]
    pattern = re.compile(r'''_\(["|'].+["|']\)''')
    column_names = [_(a[3:-2]) if pattern.match(a) else a for i, a in enumerate( values) if i%3==2 ]
    
    return ListTableNode(object_list, column_names, field_values)

class ListTableNode(template.Node):
    def __init__(self, object_list, column_names, field_values):
        self.object_list = template.Variable(object_list)
        self.column_names = column_names
        self.field_values = field_values
        
    def render(self, context):
        object_list = self.object_list.resolve(context)
        return render_to_string('listtable_columns.html', 
                                {'columns':self.column_names,
                                 'field_values':self.field_values,
                                 'object_list':object_list,'MEDIA_URL':settings.MEDIA_URL })
    
@stringfilter
@register.filter
def object_value(value, field_name):
    '''
        Return field value of the object
    '''
    ret = getattr(value, field_name, None)
    if callable(ret):
        return ret()
    return ret

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    page_numbers = [n for n in \
                    range(context['page'] - adjacent_pages, context['page'] + adjacent_pages + 1) \
                    if n > 0 and n <= context['pages']]
    return {
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
        'request': context['request']
    }

register.inclusion_tag('paginator.html', takes_context=True)(paginator)

@register.simple_tag
def page_query(page, query):
    query = query.copy()
    if 'page' in query:
        del query['page']
    query.appendlist('page', page)
    return query.urlencode()
