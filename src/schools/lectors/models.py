# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink
from schools import fix_date_boundaries

class LectorManager(models.Manager):
    def lesson_analysis(self, start, end):
        from schools.courses.models import Lesson
        from schools.companies.models import Subcount
        from collections import defaultdict #@UnresolvedImport
        from schools.lectors.models import Lector #@UnresolvedImport
        import schools

        lessons = Lesson.objects.filter(real_end__range=(start, schools.fix_date_boundaries(end)))
        
        lector_lessons = defaultdict(dict)
        
        for lesson in lessons:
            if lesson.course not in lector_lessons[lesson.real_lector]:
                lector_lessons[lesson.real_lector][lesson.course] = Subcount(lesson.course)
            subcount = lector_lessons[lesson.real_lector][lesson.course]
            subcount.length += lesson.real_minutes_length
            subcount.price += lesson.real_lector_price
            
        lectors = Lector.objects.all() 
        for lector in lectors:
            lector.analysis_courses = lector_lessons[lector].values()
            lector.analysis_length = sum([subcount.length 
                                          for subcount in lector_lessons[lector].values() ])
            lector.analysis_price = sum([subcount.price 
                                          for subcount in lector_lessons[lector].values() ])
        return lectors


# Create your models here.
class Lector(models.Model):
    objects = LectorManager()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    title = models.CharField(max_length=10, null=True, blank=True)
    
    street = models.CharField(max_length=100, null=True, blank=True)
    postal = models.CharField(max_length=5, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    
    phone = models.CharField(max_length=30, null=True, blank=True)
    mobile = models.CharField(max_length=30, null=True, blank=True)
    fax = models.CharField(max_length=30, null=True, blank=True)
    www = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'lektor'
        verbose_name_plural=u'lektori'
        
    def __unicode__(self):
        if self.title:
            return '%s, %s %s' % (self.last_name, self.first_name, self.title)
        return '%s, %s' % (self.last_name, self.first_name)
    
    @permalink
    def get_absolute_url(self):
        return ('lectors_lector_update', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_courses_url(self):
        return ('lectors_lector_courses', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_delete_url(self):
        return ('lectors_lector_delete', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_contracts_url(self):
        return ('lectors_contract_list', None, {'lector_id':str(self.pk)})
    
    @permalink
    def get_bookorders_url(self):    
        return ('lectors_lector_book_orders', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_books_url(self):
        return ('lectors_lector_books', None, {'object_id':str(self.pk)})

    
class Contract(models.Model):
    contract_number = models.CharField(max_length=30, unique=True)
    lector = models.ForeignKey('Lector')
    
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    start = models.DateField()
    end = models.DateField()
    
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'zmluva'
        verbose_name_plural=u'zmluvy'
 
    def __unicode__(self):
        return self.contract_number
        
    @permalink
    def get_absolute_url(self):
        return ('lectors_contract_update', None, {'lector_id':str(self.lector.pk), 'object_id':str(self.pk)})
        
class HourRate(models.Model):
    from schools.courses.models import Course
    contract = models.ForeignKey('Contract')
    course = models.ForeignKey(Course)
    
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'hodinová sadzba'
        verbose_name_plural=u'hodinové sadzby'
    
    def __unicode__(self):
        return unicode(self.hour_rate)
