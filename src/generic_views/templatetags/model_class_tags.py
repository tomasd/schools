from django import template
register = template.Library()

@register.simple_tag
def class_plural_name(obj):
    return obj._meta.verbose_name_plural.capitalize()