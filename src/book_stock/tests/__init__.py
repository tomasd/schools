from book_stock.forms import DeliverBookOrderForm
from book_stock.models import Book, BookOrder
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.contrib.contenttypes.models import ContentType
import decimal

class BookTest(TestCase):
    fixtures=['test_book_stock']
    def setUp(self):
        self.client.login(username='tomas', password='tomas')
        
    def testList(self):
        response = self.client.get(reverse('stock_books'))
        self.assertEquals(200, response.status_code)
        
    def testCreate(self):
        response = self.client.get(reverse('stock_book_create'))
        self.assertEquals(200, response.status_code)
        
        response = self.client.post(reverse('stock_book_create'), 
                         {'name':'xxx', 'author':'author', 'year':'2005',
                          'price':'10.50'})
        self.assertRedirects(response, reverse('stock_book_update', kwargs={'object_id':'2'}))
        
        response = self.client.get(reverse('stock_book_update', kwargs={'object_id':'2'}))
        self.assertEquals(200, response.status_code)
        
    def testDelete(self):
        response = self.client.post(reverse('stock_book_delete', kwargs={'object_id':'1'}))
        self.assertRedirects(response, reverse('stock_books'))
        self.assertTrue(len(Book.objects.filter(pk=1)) == 0)
        
class DeliverBookOrderFormTest(TestCase):
    fixtures=['test_book_stock']
    def setUp(self):
        self.client.login(username='tomas', password='tomas')
        
    def testDisplay(self):
        form = DeliverBookOrderForm()
        self.assertTrue(len(unicode(form))> 0)
        
    def testSave(self):
        form = DeliverBookOrderForm({'book_order':'1', 'stock_number':'xxx-1', 'price':'10.50','delivered':'17.3.2010'})
        self.assertTrue(form.is_valid())
        delivery = form.save()
        self.assertEquals('xxx-1', delivery.stock_object.stock_number)