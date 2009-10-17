from django.contrib import admin
from schools.courses.models import Course, CourseMember, Lesson

class CourseMemberInlineAdmin(admin.TabularInline):
    model = CourseMember

class LessonInlineAdmin(admin.TabularInline):
    model = Lesson

class CourseAdmin(admin.ModelAdmin):
    inlines = (CourseMemberInlineAdmin, LessonInlineAdmin)
    
admin.site.register(Course, CourseAdmin)