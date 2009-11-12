# Create your views here.
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object
from schools.buildings.forms import BuildingForm, ClassroomLessonsForm
from schools.buildings.models import Building, Classroom, BuildingMonthExpense
from django.utils import simplejson
from django.utils.dateformat import format

def building_update(request, object_id):
    inlines = [{'model':Classroom}, {'model':BuildingMonthExpense, 'extra':1}]
    context = {'building':get_object_or_404(Building, pk=object_id)}
    return update_object(request, model=Building, object_id=object_id, form_class=BuildingForm, extra_context=context, inlines=inlines)

def classroom_lessons(request, object_id):
    classroom = get_object_or_404(Classroom, pk=object_id)
    form = ClassroomLessonsForm(request.GET)
    lessons = classroom.plannedlessons_set.all()
    
    if form.is_valid():
        if form.cleaned_data['start']:
            lessons = lessons.filter(end__gte=form.cleaned_data['start'])
        if form.cleaned_data['end']:
            lessons = lessons.filter(start__lte=form.cleaned_data['end'])
    lessons = [{'id':a.pk,
                'start':format(a.start, 'Y-m-d\TH:i:s.000O'), 
                'end':format(a.end, 'Y-m-d\TH:i:s.000O'),
                'title':unicode(a.course)} for a in lessons]
    text = simplejson.dumps(lessons)
    return HttpResponse(text, mimetype='application/json')