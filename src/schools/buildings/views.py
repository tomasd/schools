# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.utils.dateformat import format
from generic_views.views.create_update import update_object, create_object
from generic_views.views.delete import delete_object
from schools import fix_date_boundaries, permission_required
from schools.buildings.forms import BuildingForm, ClassroomLessonsForm
from schools.buildings.models import Building, Classroom, BuildingMonthExpense
from schools.search.views import object_list

@permission_required('buildings.add_building')
def building_create(*args, **kwargs):
    return create_object(*args, **kwargs)

@permission_required('buildings.change_building')
def building_update(request, object_id):
    inlines = [{'model':Classroom}, {'model':BuildingMonthExpense, 'extra':1}]
    context = {'building':get_object_or_404(Building, pk=object_id)}
    return update_object(request, model=Building, object_id=object_id, form_class=BuildingForm, extra_context=context, inlines=inlines)

@permission_required('buildings.delete_building')
def building_delete(*args, **kwargs):
    return delete_object(*args, **kwargs)

@permission_required('buildings.add_building', 'buildings.change_building', 'buildings.delete_building')
def building_list(*args, **kwargs):
    return object_list(*args, **kwargs)

def classroom_lessons(request, object_id):
    '''
        Filter classrooms and export them in JSON format.
    '''
    classroom = get_object_or_404(Classroom, pk=object_id)
    form = ClassroomLessonsForm(request.GET)
    lessons = classroom.plannedlessons_set.all()
    
    if form.is_valid():
        if form.cleaned_data['start']:
            lessons = lessons.filter(end__gte=form.cleaned_data['start'])
        if form.cleaned_data['end']:
            lessons = lessons.filter(start__lt=fix_date_boundaries(form.cleaned_data['end']))
    lessons = [{'id':a.pk,
                'start':format(a.start, 'Y-m-d\TH:i:s.000O'),
                'end':format(a.end, 'Y-m-d\TH:i:s.000O'),
                'title':unicode(a.course)} for a in lessons]
    text = simplejson.dumps(lessons)
    return HttpResponse(text, mimetype='application/json')
