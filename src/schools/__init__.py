from datetime import timedelta
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.db.models.query_utils import CollectedObjects
import operator

def get_related_objects(obj):
    '''
        Return all related objects to this object. These objects
        will be deleted when the object is deleted.
        
        Return form is
        [(ModelClass, {id, instance}),]
    '''
    seen_objects = CollectedObjects()
    obj._collect_sub_objects(seen_objects)
    return seen_objects.items()

def has_related_objects(obj):
    '''
        Return true if object has some related objects.
    '''
    return sum([len(a[1]) for a in get_related_objects(obj)]) == 0

def fix_date_boundaries(date):
    return date + timedelta(days=1)

def permission_required(*args, **kwargs):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    """
    def _test(user):
        return reduce(operator.or_, [user.has_perm(p) for p in args])
    return user_passes_test(_test, login_url=kwargs.get('login_url', None))