# Create your views here.
from generic_views.views.create_update import update_object
from django.shortcuts import get_object_or_404
from schools.students.models import Student

def update_student(request, object_id):
    return update_object(request, object_id=object_id, model=Student, extra_context={'student':get_object_or_404(Student, pk=object_id)})