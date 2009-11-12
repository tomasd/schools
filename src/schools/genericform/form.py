from django.forms import models
from django.forms.models import ModelForm, ModelFormMetaclass

def modelform_factory(model, form=ModelForm, fields=None, exclude=None,
                       formfield_callback=lambda f: f.formfield()):
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.

    # Build up a list of attributes that the Meta object will have.
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    parent = (object,)
    if hasattr(form, 'Meta'):
        parent = (form.Meta, object)
    Meta = type('Meta', parent, attrs)

    # Give this new form class a reasonable name.
    class_name = model.__name__ + 'Form'

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }
    form_class = form
    if isinstance(form, PreProcessForm):
        form_class = form.form_class
        
    f = ModelFormMetaclass(class_name, (form_class,), form_class_attrs)
    if isinstance(form, PreProcessForm):
        return PreProcessForm(f, form.function)
    return f
old_modelform_factory = models.modelform_factory
models.modelform_factory = modelform_factory

class PreProcessForm(object):
    def __init__(self, form_class, function):
        super(PreProcessForm, self).__init__()
        self.form_class = form_class
        self.function = function
  
    def __call__(self, *args, **kwargs):
        form = self.form_class(*args, **kwargs)
        self.function(form)
        return form
    
    def __getattr__(self, name):
        return getattr(self.form_class, name)