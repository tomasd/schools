from django.contrib import admin
from schools.buildings.models import Building, Classroom, BuildingMonthExpense

class ClassroomInline(admin.TabularInline):
    model = Classroom

class BuildingMonthExpenseInline(admin.TabularInline):
    model = BuildingMonthExpense
        
    
class BuildingAdmin(admin.ModelAdmin):
    inlines = (ClassroomInline, BuildingMonthExpenseInline)
admin.site.register(Building, BuildingAdmin)
