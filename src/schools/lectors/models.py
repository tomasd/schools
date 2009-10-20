# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink

# Create your models here.
class Lector(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    
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
    def __unicode__(self):
        if self.title:
            return '%s, %s %s' % (self.last_name, self.first_name, self.title)
        return '%s, %s' % (self.last_name, self.first_name)
    
    @permalink
    def get_absolute_url(self):
        return ('lectors_lector_update', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_contracts_url(self):
        return ('lectors_contract_list', None, {'lector_id':str(self.pk)})
    
class Contract(models.Model):
    contract_number = models.CharField(max_length=30, unique=True)
    lector = models.ForeignKey('Lector')
    
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    start = models.DateField()
    end = models.DateField()
    
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
 
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
    
    def __unicode__(self):
        return unicode(self.hour_rate)