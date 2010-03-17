from book_stock.models import BookOrder, Book, StockObject, BookDelivery
from django.contrib import admin

admin.site.register(BookOrder)
admin.site.register(Book)
admin.site.register(StockObject)
admin.site.register(BookDelivery)