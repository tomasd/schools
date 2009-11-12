# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db import models
from django.db.models import permalink
from django.db.models.query_utils import Q
from calendar import monthrange
import calendar
import datetime

# Create your models here.
class Classroom(models.Model):
    name = models.CharField(max_length=100)
    infinite_room = models.BooleanField(default=False)
    
    building = models.ForeignKey('Building')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('buildings_classroom_update', None, {'object_id':str(self.pk)})
    
    
class Building(models.Model):
    name = models.CharField(max_length=100)
    
    street = models.CharField(max_length=100, null=True, blank=True)
    postal = models.CharField(max_length=5, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('buildings_building_update', None, {'object_id':str(self.pk)})
    
    def building_price_for(self, start_date, end_date):
        price = Decimal(0)
        for start, end in iter_months(start_date, end_date):
            expenses = BuildingMonthExpense.objects.filter(Q(end__isnull=True)|Q(end__gte=start), start__lte=end)
            if expenses:
                expense = expenses[0]
                days = Decimal((end-start).days + 1)
                price += (days/Decimal(monthrange(start.year, start.month)[1])) * expense.price
        return price

def iter_months(start, end):        
    while start < end:
        r = calendar.monthrange(start.year, start.month)
        yield start, min(datetime.date(start.year, start.month, r[1]), end)
        start += datetime.timedelta(days=r[1] - start.day + 1)
        
    
class BuildingMonthExpense(models.Model):
    building = models.ForeignKey('Building')
    
    start = models.DateField()
    end = models.DateField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        fmt = '%d.%m.%Y'
        return u'%s - %s: %.2f €' % (format(self.start, fmt), format(self.end, fmt), self.price)
    
    @permalink
    def get_absolute_url(self):
        return ('buildings_buildingmonthexpense_update', None, {'object_id':str(self.pk)})