# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object, create_object
from schools.search.views import object_list
from schools.students.models import Student
from generic_views.views.delete import delete_object
from schools import permission_required
from schools.students.forms import StudentForm

@permission_required('students.add_student')
def student_create(*args, **kwargs):
    return create_object(*args, **kwargs)

@permission_required('students.change_student')
def student_update(request, object_id):
    return update_object(request, object_id=object_id, model=Student, 
                         form_class=StudentForm,
                         extra_context={'student':get_object_or_404(Student, pk=object_id)})

@permission_required('students.delete_student')
def student_delete(*args, **kwargs):
    return delete_object(*args, **kwargs)

@permission_required('students.delete_student', 'students.change_student', 'students.add_student')
def student_list(*args, **kwargs):
    return object_list(*args, **kwargs)

def student_courses(request, object_id):
    student = get_object_or_404(Student, pk=object_id)
    queryset = student.coursemember_set.all()
    return object_list(request, ('course__name__contains',) , queryset=queryset, template_name='students/student_courses_list.html', extra_context={'student':student})
