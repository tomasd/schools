from django.db import models

# Create your models here.
class CourseMemberReference(models.Model):
    from schools.courses.models import CourseMember
    date = models.DateField()
    text = models.TextField()
    course_member = models.ForeignKey(CourseMember)