"""Create and Update views with inlines."""
from django import http
from django.contrib.auth.views import redirect_to_login
from django.core.xheaders import populate_xheaders
from django.forms.forms import BaseForm
from django.forms.formsets import all_valid
from django.forms.models import inlineformset_factory
from django.template import loader, RequestContext
from django.utils.translation import ugettext
from django.views.generic.create_update import get_model_and_form_class, \
    lookup_object, redirect, apply_extra_context

__all__ = ('create_object', 'update_object')

#def my_view(request):
#
#     class MyModelForm(ModelForm):
#         class Meta:
#             model = MyModel
#
#         def __init__(self, *args, **kwargs):
#             kwargs['initial'] = {'field1': request.GET.get('field1','')}
#             return super(MyModelForm, self).__init__(*args, **kwargs)
#
#     return create_object(request, form_class=MyModelForm)


def create_object(request, model=None, template_name=None,
        template_loader=loader, extra_context=None, post_save_redirect=None,
        login_required=False, context_processors=None, form_class=None,
        inlines=None, initial={}, preprocess_form=lambda _:_):
    """
    Generic object-creation function with inlines capability.

    Templates: ``<app_label>/<model_name>_form.html``
    Context:
        form
            the form for the object
        xxx_formset
            ModelFormSet for model classes in ``inlines`` argument.
    """
    if extra_context is None:
        extra_context = {}
    if inlines is None:
        inlines = ()
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)
    formset_classes = []
    formsets = []
    
    tmodel, form_class = get_model_and_form_class(model, form_class)
    if True or issubclass(form_class, BaseForm):
        class InitialModelForm(form_class):
            class Meta:
                model = tmodel
    
            def __init__(self, *args, **kwargs):
                request_initial = dict(request.GET.items())
                request_initial.update(initial)
                kwargs['initial'] = request_initial#{'field1': request.GET.get('field1','')}
                return super(InitialModelForm, self).__init__(*args, **kwargs)
        form_class = InitialModelForm
    model = tmodel
    
    for inline in inlines:
        formset_classes.append(inlineformset_factory(model, **inline))

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        preprocess_form(form)
        if form.is_valid():
            form_validated = True
            new_object = form.save()
        else:
            form_validated = False
            new_object = model()
            
        for klass in formset_classes:
            formset = klass(request.POST, request.FILES, instance=new_object)
            formsets.append(formset)

        if all_valid(formsets) and form_validated:
            new_object.save()
            for formset in formsets:
                formset.save()

            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The "
                    "%(verbose_name)s was created successfully.") % 
                        {"verbose_name": model._meta.verbose_name})
            return redirect(post_save_redirect, new_object)
    else:

        form = form_class()
        preprocess_form(form)
        for klass in formset_classes:
            formset = klass()
            formsets.append(formset)

    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label, 
            model._meta.object_name.lower())
    template = template_loader.get_template(template_name)
    context = RequestContext(request, {
        'form': form,
    }, context_processors)
    apply_extra_context(extra_context, context)
    for formset in formsets:
        key = '%s_formset' % formset.model._meta.object_name.lower()
        context[key] = formset
    return http.HttpResponse(template.render(context))

def update_object(request, model=None, object_id=None, slug=None,
        slug_field='slug', template_name=None, template_loader=loader,
        extra_context=None, post_save_redirect=None, login_required=False,
        context_processors=None, template_object_name='object',
        form_class=None, inlines=None, obj=None, preprocess_form=lambda _:_, preprocess_formset=lambda _:_):
    """
    Generic object-update function with inlines.

    Templates: ``<app_label>/<model_name>_form.html``
    Context:
        form
            the form for the object
        object
            the original object being edited
        xxx_formset
            ModelFormSet for model classes in ``inlines`` argument.
    """
    if extra_context is None:
        extra_context = {}
    if inlines is None:
        inlines = ()
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)
    formset_classes = []
    formsets = []

    model, form_class = get_model_and_form_class(model, form_class)
    if obj is None:
        obj = lookup_object(model, object_id, slug, slug_field)

    for inline in inlines:
        formset_classes.append(inlineformset_factory(model, **inline))

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        preprocess_form(form)
        if form.is_valid():
            form_validated = True
            new_object = form.save()
        else:
            form_validated = False
            new_object = obj

        for klass in formset_classes:
            formset = klass(request.POST, request.FILES, instance=new_object)
            preprocess_formset(formset)
            formsets.append(formset)

        if all_valid(formsets) and form_validated:
            new_object.save()
            for formset in formsets:
                formset.save()

            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The "
                    "%(verbose_name)s was updated successfully.") % 
                        {"verbose_name": model._meta.verbose_name})
            return redirect(post_save_redirect, new_object)
    else:
        form = form_class(instance=obj)
        preprocess_form(form)
        for klass in formset_classes:
            formset = klass(instance=obj)
            preprocess_formset(formset)
            formsets.append(formset)

    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label,
            model._meta.object_name.lower())
    template = template_loader.get_template(template_name)
    context = RequestContext(request, {
        'form': form,
        template_object_name: obj,
    }, context_processors)
    apply_extra_context(extra_context, context)
    for formset in formsets:
        key = '%s_formset' % formset.model._meta.object_name.lower()
        context[key] = formset
    response = http.HttpResponse(template.render(context))
    populate_xheaders(request, response, model, getattr(obj,
        obj._meta.pk.name))
    return response

# vim: ai ts=4 sts=4 et sw=4
