from django import template
from book_stock.forms import CreateBookOrderForm
from django.template import Variable

register = template.Library()

@register.tag
def stock_form(parser, token):
    try:
        tag_name, _for_, object_name, _as_, varname = token.split_contents() #@UnusedVariable
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 2 argument' % token.contents.split()[0:])
    
    return StockFormNode(object_name, varname)

class  StockFormNode(template.Node):
    def __init__(self, object_name, varname):
        self.object_name = Variable(object_name)
        self.varname = varname
        
    def render(self, context):
        person = self.object_name.resolve(context)
        context[self.varname] = CreateBookOrderForm(person)
        return ''