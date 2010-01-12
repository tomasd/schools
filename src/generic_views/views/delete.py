from django.core.urlresolvers import reverse
from django.template import loader
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext
from django.views.generic.create_update import delete_object as _delete_object, \
    lookup_object

def delete_object(request, model, post_delete_redirect, object_id=None,
        slug=None, slug_field='slug', template_name=None,
        template_loader=loader, extra_context=None, login_required=False,
        context_processors=None, template_object_name='object', post_delete_redirect_args=()):
    '''
        Uses generic view. Only difference is that instead of 
        post_delete_redirect, this will reverse the url at first
        
        original:
        def delete_object(request, model, post_delete_redirect, object_id=None,
            slug=None, slug_field='slug', template_name=None,
            template_loader=loader, extra_context=None, login_required=False,
            context_processors=None, template_object_name='object')
    '''
    post_delete_redirect = reverse(post_delete_redirect, args=post_delete_redirect_args)
    obj = lookup_object(model, object_id, slug, slug_field)
    if hasattr(obj, 'can_remove'):
        if not obj.can_remove():
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("Object %(verbose_name)s can't be removed.") % {"verbose_name": model._meta.verbose_name})
            return HttpResponseRedirect(post_delete_redirect)
    return _delete_object(request, model=model, post_delete_redirect=post_delete_redirect, object_id=object_id,
        slug=slug, slug_field=slug_field, template_name=template_name,
        template_loader=template_loader, extra_context=extra_context, login_required=login_required,
        context_processors=context_processors, template_object_name=template_object_name)