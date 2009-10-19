# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object
from schools.buildings.forms import BuildingForm
from schools.buildings.models import Building, Classroom, BuildingMonthExpense

def building_update(request, object_id):
    inlines = [{'model':Classroom}, {'model':BuildingMonthExpense, 'extra':1}]
    context = {'building':get_object_or_404(Building, pk=object_id)}
    return update_object(request, model=Building, object_id=object_id, form_class=BuildingForm, extra_context=context, inlines=inlines)
