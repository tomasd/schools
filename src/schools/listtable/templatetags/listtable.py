from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag('listtable.html', takes_context=True)
def listtable(context, object_list, column_name):
    d = {'main_column':column_name}
    context.update(d)
    return context

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
