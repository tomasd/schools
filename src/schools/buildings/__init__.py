from schools.buildings.models import Building, Classroom

def classroom_buildings(field):
    default = []
    if field.empty_label is not None:
            default = [(u"", field.empty_label)]
    field._choices = default + [(unicode(a), [(b.pk, unicode(b)) for b in a.classroom_set.all()]) for a in Building.objects.all()]
    field.queryset = Classroom.objects.all()