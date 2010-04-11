from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import permalink
from django.core.urlresolvers import reverse

# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True, null=True)
    year = models.CharField(max_length=20, blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    @permalink
    def get_absolute_url(self):
        return ('stock_book_update', None, {'object_id':str(self.pk)})
    
    def __unicode__(self):
        if self.author and self.name and self.year:
            return '%s: %s, %s' % (self.author, self.name, self.year)
        
        if self.author and self.name:
            return '%s: %' % (self.author, self.name)
        
        return self.name
            
    
    
class StockObject(models.Model):
    book = models.ForeignKey('Book')
    stock_number = models.CharField(max_length=10, blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.stock_number, self.book)
    
class BookDelivery(models.Model):
    stock_object = models.ForeignKey('StockObject')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    book_order = models.ForeignKey('BookOrder', null=True, blank=True)
    delivered = models.DateField()
    returned = models.DateField(null=True, blank=True)
    
    person_type = models.ForeignKey(ContentType)
    person_id = models.PositiveIntegerField()
    person = generic.GenericForeignKey('person_type', 'person_id')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions = (
            ("can_return_book", ("Can return the book")),
        )
    
    def __unicode__(self):
        return u'%s - %s' % (self.person, self.stock_object)
    
    @property
    def book_full(self):
        book = self.stock_object.book
        if book.author and book.name and book.year:
            return '%s: %s, %s' % (book.author, book.name, book.year)
        if book.author and book.name:
            return '%s: %s' % (book.author, book.name)
        return book.name
    
    @property
    def book(self):
        return self.stock_object.book
    
    @property
    def book_author(self):
        return self.stock_object.book.author
    
    @property
    def book_name(self):
        return self.stock_object.book.name
    
    @property
    def book_year(self):
        return self.stock_object.book.year
    
    def get_returnbook_url(self):
        from book_stock.views import return_book
        return reverse(return_book, kwargs={'object_id':str(self.pk)})
    
    @permalink
    def get_absolute_url(self):
        return ('stock_book_delivery', None, {'object_id':str(self.pk)})
    
    
class BookOrder(models.Model):
    book = models.ForeignKey('Book')
    person_type = models.ForeignKey(ContentType)
    person_id = models.PositiveIntegerField()
    person = generic.GenericForeignKey('person_type', 'person_id')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.person, self.book)
