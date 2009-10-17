import IPython.ipapi #@UnresolvedImport
ip = IPython.ipapi.get()

def load_django_models():
    try:
        from django.db.models.loading import get_models
        for m in get_models():
            try:
                ip.ex("from %s import %s" % (m.__module__, m.__name__))
            except ImportError:
                print "ERROR: Import of %s from %s failed." % (m.__name__, m.__module__)                
                pass
        print 'INFO: Loaded Django models.'
    except ImportError:
        pass

def init_django():
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

    from django.db import models
    for name in dir(models):
        if not name.startswith('_'):
            ip.user_ns[name] = getattr(models, name)
    load_django_models()
    from django.core.urlresolvers import reverse
    from django.test import Client
    ip.user_ns['client'] = Client()
    ip.user_ns['reverse'] = reverse
    
    print 'INFO: Created client instance.'

init_django()
