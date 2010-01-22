# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from schools.students.models import Student

def studentbook(request):
    student = get_object_or_404(Student, user=request.user)
    return render_to_response('studentbook/studentbook.html', {'student':student}, context_instance=RequestContext(request))
