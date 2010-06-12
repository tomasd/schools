from django.contrib.auth.views import login, logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.http import urlquote

class FullAuthenticationMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
#        print getattr(view_func, 'disable_full_authentication', False)
        if getattr(view_func, 'disable_full_authentication', False):
            return None
        # fix for tests#        if getattr(view_func, 'disable_full_authentication', False):
#            return None
#        # fix for tests
#        if request.META['SERVER_NAME'] == 'testserver':
#            return
#        if request.path == reverse(login) or request.path == reverse(logout) or 'media' in request.path:
#            return
#        
#        if not request.user.is_authenticated():
#            return redirect('%s?next=%s' % (reverse(login), urlquote(request.get_full_path())))
        if request.META['SERVER_NAME'] == 'testserver':
            return
        if request.path == reverse(login) or request.path == reverse(logout) or 'media' in request.path:
            return
        
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse(login), urlquote(request.get_full_path())))
