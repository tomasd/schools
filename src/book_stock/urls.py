from django.conf.urls.defaults import patterns, url
from generic_views.views.create_update import create_object, update_object
from book_stock.models import Book, BookOrder
from django.views.generic.list_detail import object_list
from book_stock.views import return_book

urlpatterns = patterns('book_stock.views',
    url(r'book/create/$', create_object, kwargs={'model':Book}, name='stock_book_create'),
    url(r'book/$', object_list, kwargs={'queryset':Book.objects.all()}, name='stock_books'),
    url(r'book/(?P<object_id>\d+)/$', update_object, kwargs={'model':Book}, name='stock_book_update'),
    url(r'book/(?P<object_id>\d+)/delete/$', 'delete_book', kwargs={'model':Book}, name='stock_book_delete'),
    url(r'book-delivery/(?P<object_id>\d+)/return/$', return_book),
    url(r'book-order/$', object_list, {'queryset':BookOrder.objects.filter(bookdelivery__pk__isnull=True)}, name='stock_book_orders'),
    url(r'book-order/delivery/$', 'deliver_orders', name='stock_book_orders_delivery'),
)
