# imports # {{{
from django.utils import simplejson
from django.http import HttpResponse, Http404
from django.utils.functional import Promise
from django.utils.translation import force_unicode
from django.utils.simplejson import JSONEncoder
from django.conf import settings
# }}}

# JSONResponse # {{{
class LazyEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyEncoder, self).default(o)

class JSONResponse(HttpResponse):
    def __init__(self, data):
        HttpResponse.__init__(
            self, content=simplejson.dumps(data, cls=LazyEncoder),
            #mimetype="text/html",
        ) 
# }}}

# ajax_form_handler # {{{
def ajax_form_handler(
    request, form_cls, require_login=True, allow_get=settings.DEBUG
):
    if require_login and not request.user.is_authenticated(): 
        raise Http404("login required")
    if not allow_get and request.method != "POST":
        raise Http404("only post allowed")
    if isinstance(form_cls, basestring):
        # can take form_cls of the form: "project.app.forms.FormName"
        from django.core.urlresolvers import get_mod_func
        mod_name, form_name = get_mod_func(form_cls)
        form_cls = getattr(__import__(mod_name, {}, {}, ['']), form_name)
    form = form_cls(request, request.REQUEST)
    if form.is_valid():
        return JSONResponse({ 'success': True, 'response': form.save() })
    return JSONResponse({ 'success': False, 'errors': form.errors })
# }}}
