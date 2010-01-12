from django import template
from django.template import Variable
from schools import get_related_objects
from django.utils.safestring import mark_safe

register=template.Library() 

@register.tag
def candelete(parser, token):
    try:
        tag_name, object_name = token.split_contents() #@UnusedVariable
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 1 argument' % token.contents.split()[0:])
    body = parser.parse(('endcandelete',))
    parser.delete_first_token()
    return CanDeleteNode(object_name, body)

class CanDeleteNode(template.Node):
    def __init__(self, object_name, body):
        self.object_name = Variable(object_name)
        self.body = body
        
    def render(self, context):
        object = self.object_name.resolve(context)
        if object is not None:
            if hasattr(object, 'get_delete_url'):
                if hasattr(object, 'can_remove'):
                    if not getattr(object, 'can_remove'):
                        return ''
                return self.body.render(context)
            

@register.inclusion_tag('generic_views/related_objects.html')
def related_objects_list(obj):
    return {'related_objects':get_related_objects(obj)}

