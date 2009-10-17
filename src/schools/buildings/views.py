# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from schools.buildings.models import Building, Classroom, BuildingMonthExpense
from schools.buildings.forms import BuildingForm
from django.forms.models import inlineformset_factory
def building_update(request, object_id):
    building = get_object_or_404(Building, pk=object_id)

    ClassroomFormset = inlineformset_factory(Building, Classroom, extra=1, )
    BuildingMonthExpenseFormset = inlineformset_factory(Building, BuildingMonthExpense, extra=1, )
    
    if request.method== 'POST':
        building_form = BuildingForm(data=request.POST, instance=building)
        classroom_formset = ClassroomFormset(data=request.POST, instance=building)
        buildingmonthexpense_formset = BuildingMonthExpenseFormset(data=request.POST, instance=building)
        
        if building_form.is_valid() and classroom_formset.is_valid() and buildingmonthexpense_formset.is_valid():
            building_form.save()
            classroom_formset.save()
            buildingmonthexpense_formset.save()
            return redirect(building)
    
    building_form = BuildingForm(instance=building)
    classroom_formset = ClassroomFormset(instance=building)
    buildingmonthexpense_formset = BuildingMonthExpenseFormset(instance=building)
    
    context = {'building_form':building_form,
               'classroom_formset':classroom_formset,
               'buildingmonthexpense_formset':buildingmonthexpense_formset}
    return render_to_response('buildings/building_form.html', 
                  RequestContext(request, context))