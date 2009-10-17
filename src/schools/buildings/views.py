# Create your views here.
from schools.buildings.models import Building, Classroom, BuildingMonthExpense
from schools.buildings.forms import BuildingForm
from generic_views.views.create_update import update_object
def building_update(request, object_id):
    inlines = [{'model':Classroom}, {'model':BuildingMonthExpense, 'extra':1}]
    return update_object(request, model=Building, object_id=object_id, form_class=BuildingForm, inlines=inlines)