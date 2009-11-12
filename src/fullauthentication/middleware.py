from django.contrib.auth.views import login, logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.static import serve
from django.utils.http import urlencode, urlquote
class FullAuthenticationMiddleware(object):
    def process_request(self, request):
        if request.path == reverse(login) or request.path == reverse(logout) or 'media' in request.path:
            return
        
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse(login), urlquote(request.get_full_path())))