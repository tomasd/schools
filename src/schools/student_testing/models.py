from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.utils import dateformat

# Create your models here.
class StudentTest(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    max_score = models.IntegerField()
    language = models.CharField(max_length=2, choices=settings.SCHOOL_LANGUAGES)
    
    def __unicode__(self):
        return self.name
    
class TestingTerm(models.Model):
    from schools.courses.models import Course
    date = models.DateField()
    test = models.ForeignKey('StudentTest')
    course = models.ForeignKey(Course)
    
    def __unicode__(self):
        start_format = 'd.m.Y'
        return '%s - %s' % (self.test, dateformat.format(self.date, start_format))
    
    @permalink
    def get_absolute_url(self):
        return ('courses_course_test_result_update', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})
    
    
class TestResult(models.Model):
    from schools.courses.models import CourseMember
    testing_term = models.ForeignKey('TestingTerm')
    course_member = models.ForeignKey(CourseMember)
    score = models.IntegerField()
    description = models.TextField(blank=True)
    
    @property
    def test(self):
        return self.testing_term.test