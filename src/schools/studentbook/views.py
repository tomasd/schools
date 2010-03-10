# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from schools.lectors.models import Lector
from schools.students.models import Student
from threadedcomments.forms import ThreadedCommentForm

def studentbook(request):
    student = get_object_or_404(Student, user=request.user)
    lectors = Lector.objects.filter(lesson__lessonattendee__course_member__student=student).distinct()
    return render_to_response('studentbook/studentbook.html', 
                          {'student':student, 'lectors':lectors}, context_instance=RequestContext(request))
    
def lector(request, object_id):
    student = get_object_or_404(Student, user=request.user)
    lector = get_object_or_404(Lector.objects.filter(lesson__lessonattendee__course_member__student=student).distinct(), pk=object_id)
    return render_to_response('studentbook/lector.html',
                              {'lector':lector, 'form':ThreadedCommentForm()}, context_instance=RequestContext(request))
