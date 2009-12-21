# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object
from schools.search.views import object_list
from schools.students.models import Student

def update_student(request, object_id):
    return update_object(request, object_id=object_id, model=Student, extra_context={'student':get_object_or_404(Student, pk=object_id)})

def student_courses(request, object_id):
    student = get_object_or_404(Student, pk=object_id)
    queryset = student.coursemember_set.all()
    return object_list(request, ('course__name__contains',) ,queryset=queryset, template_name='students/student_courses_list.html', extra_context={'student':student})