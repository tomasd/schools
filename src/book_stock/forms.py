from book_stock.models import Book, BookOrder, StockObject, BookDelivery
from django import forms
from django.forms.widgets import HiddenInput
import datetime

class CreateBookOrderForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Book.objects.all())
    
    def __init__(self, person, *args, **kwargs):
        super(CreateBookOrderForm, self).__init__(*args, **kwargs)
        self.person = person
        
    def save(self):
        order = BookOrder(book=self.cleaned_data['book'], person=self.person)
        order.save()
        return order
    
class DeliverBookOrderForm(forms.Form):
    book_order = forms.ModelChoiceField(queryset=BookOrder.objects.all(), widget=HiddenInput)
    stock_number = forms.CharField()
    price = forms.DecimalField()
    delivered = forms.DateField()
    
    def __init__(self, *args, **kwargs):
        super(DeliverBookOrderForm, self).__init__(*args, **kwargs)
        if 'book_order' in kwargs.get('initial', {}):
            self.book_order_object = BookOrder.objects.get(pk=kwargs['initial']['book_order'])
            if 'price' not in kwargs.get('initial', {}):
                self.fields['price'].initial = self.book_order_object.book.price 
        if 'delivered' not in kwargs.get('initial', {}):
            self.fields['delivered'].initial = datetime.date.today() 
    
    def save(self):
        book_order = self.cleaned_data['book_order']
        price = self.cleaned_data['price']
        stock_object = StockObject(book=book_order.book, price=price,
                                    stock_number=self.cleaned_data['stock_number'])
        stock_object.save()
        delivery = BookDelivery(stock_object=stock_object, price=price, 
                                book_order=book_order, delivered=self.cleaned_data['delivered'],
                                person=book_order.person)
        delivery.save()
        return delivery