from django import template
from django.template import Variable
from schools import get_related_objects

register = template.Library() 

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
            if not user_has_permission(context['user'], 'delete', object):
                return ''
            if hasattr(object, 'get_delete_url'):
                if hasattr(object, 'can_remove'):
                    if not getattr(object, 'can_remove'):
                        return ''
                return self.body.render(context)
        return ''

@register.tag
def entitylink(parser, token):
    try:
        tag_name, object_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 1 argument' % token.contents.split()[0:])
    return EntityLinkNode(object_name)
    
class EntityLinkNode(template.Node):
    def __init__(self, object_name):
        self.object_name = Variable(object_name)
        
    def render(self, context):
        object = self.object_name.resolve(context)
        if object is not None:
            if user_has_permission(context['user'], 'change', object):
                return u'<a href="%s">%s</a>' % (object.get_absolute_url(), object)
            return unicode(object)
        
    

@register.tag
def canchange(parser, token):
    try:
        tag_name, object_name = token.split_contents() #@UnusedVariable
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 1 argument' % token.contents.split()[0:])
    body = parser.parse(('else', 'endcanchange',))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endcanchange',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return CanChangeNode(object_name, body, nodelist_false)

class CanChangeNode(template.Node):
    def __init__(self, object_name, body, nodelist_false):
        self.object_name = Variable(object_name)
        self.body = body
        self.nodelist_false = nodelist_false
        
    def render(self, context):
        object = self.object_name.resolve(context)
        if object is not None:
            if user_has_permission(context['user'], 'change', object):
                return self.body.render(context)
            return self.nodelist_false.render(context)
        
@register.tag
def hasmoduleperms(parser, token):
    try:
        tag_name, module_name = token.split_contents() #@UnusedVariable
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 1 argument' % token.contents.split()[0:])
    body = parser.parse(('else', 'endhasmoduleperms',))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endhasmoduleperms',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return HasModulePermsNode(module_name, body, nodelist_false)

class HasModulePermsNode(template.Node):
    def __init__(self, module_name, body, nodelist_false):
        self.module_name =module_name
        self.body = body
        self.nodelist_false = nodelist_false
        
    def render(self, context):
        if object is not None:
            if context['user'].has_module_perms(self.module_name):
                return self.body.render(context)
            return self.nodelist_false.render(context)
            
def user_has_permission(user, right, object):
    return user.has_perm('%s.%s_%s' % (object._meta.app_label, right, object.__class__.__name__.lower()))

@register.inclusion_tag('generic_views/related_objects.html')
def related_objects_list(obj):
    return {'related_objects':get_related_objects(obj)}

