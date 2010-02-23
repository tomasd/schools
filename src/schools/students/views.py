# Create your views here.
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from generic_views.views.create_update import update_object, create_object
from generic_views.views.delete import delete_object
from schools import permission_required
from schools.search.views import object_list
from schools.students.forms import StudentForm
from schools.students.models import Student

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

def student_user_set_password(request, object_id):
    user = get_object_or_404(User, student=object_id)
    student = get_object_or_404(Student, pk=object_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("Heslo pre studenta bolo nastavene"))
            return redirect(student)
    else:
        form = SetPasswordForm(user)
    return render_to_response('students/set_password.html', 
                              {'student':student, 'form':form}, context_instance=RequestContext(request))
    