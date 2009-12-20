from django.db.models.query_utils import CollectedObjects

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