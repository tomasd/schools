from django.contrib import admin
from schools.courses.models import Course, CourseMember, Lesson,\
    ReasonForNotRealizing

class CourseMemberInlineAdmin(admin.TabularInline):
    model = CourseMember

class LessonInlineAdmin(admin.TabularInline):
    model = Lesson

class CourseAdmin(admin.ModelAdmin):
    inlines = (CourseMemberInlineAdmin, LessonInlineAdmin)
    
admin.site.register(Course, CourseAdmin)
admin.site.register(ReasonForNotRealizing)