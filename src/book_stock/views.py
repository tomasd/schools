# Create your views here.
from book_stock.forms import CreateBookOrderForm, DeliverBookOrderForm, \
    CreateBookOrderForPersonsForm
from book_stock.models import BookOrder, BookDelivery
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext
from django.views.decorators.http import require_POST, require_GET
from django.views.generic.create_update import delete_object
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
import datetime

def person_orders(request, object_id, model, person_object_name='person', *args, **kwargs):
    '''
        Orders for the person.
    '''
    person = get_object_or_404(model, pk=object_id)
    if request.method == 'POST':
        form = CreateBookOrderForm(person, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.get_full_path())
    else:
        form = CreateBookOrderForm(person)
        
    person_type = ContentType.objects.get_for_model(person)
    queryset = BookOrder.objects.filter(person_type__pk=person_type.pk, person_id=person.pk)
    extra_context = kwargs.pop('extra_context') if 'extra_context' in kwargs else {}
    extra_context['person'] = person
    extra_context[person_object_name] = person
    extra_context['form'] = form
    return object_list(request, queryset=queryset, extra_context=extra_context, *args, **kwargs)

def persons_orders(request, persons, *args, **kwargs):
    '''
        Orders for multiple persons.
    '''
    if request.method == 'POST':
        form = CreateBookOrderForPersonsForm(persons, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.get_full_path())
    else:
        form = CreateBookOrderForPersonsForm(persons)
        
    person_type = ContentType.objects.get_for_model(persons.model)
    queryset = BookOrder.objects.filter(person_id__in=(a.pk for a in persons), person_type=person_type)
    extra_context = kwargs.pop('extra_context', {})
    extra_context['form'] = form
    return object_list(request, queryset=queryset, extra_context=extra_context, *args, **kwargs)

def person_books(request, object_id, model, person_object_name='person', *args, **kwargs):
    '''
        Books delivered to the person.
    '''
    person = get_object_or_404(model, pk=object_id)
    person_type = ContentType.objects.get_for_model(person)
    queryset = BookDelivery.objects.filter(person_type__pk=person_type.pk, person_id=person.pk)
    extra_context = kwargs.pop('extra_context') if 'extra_context' in kwargs else {}
    extra_context['person'] = person
    extra_context[person_object_name] = person
    return object_list(request, queryset=queryset, extra_context=extra_context, *args, **kwargs)

@permission_required('book_stock.delete_book')
def delete_book(request, *args, **kwargs):
    post_delete_redirect = reverse('stock_books')
    return delete_object(request, post_delete_redirect=post_delete_redirect, *args, **kwargs)

@permission_required('book_stock.can_return_book')
@require_POST
def return_book(request, object_id):
    book = get_object_or_404(BookDelivery, pk=object_id)
    book.returned = datetime.date.today()
    book.save()
    return redirect(request.META.get('HTTP_REFERER', request.POST.get('next', '/')))

@require_GET
def _deliver_orders_GET(request, orders):
    FormSet = formset_factory(DeliverBookOrderForm, extra=0)
    formset = FormSet(initial=[{'book_order':str(a.pk)} for a in orders])
    return render_to_response('book_stock/deliver_orders.html',
                      {'orders':orders, 'formset':formset},
                      context_instance=RequestContext(request))
    
@require_POST
def _deliver_orders_POST(request, orders):
    FormSet = formset_factory(DeliverBookOrderForm, extra=0)
    formset = FormSet(data=request.POST, initial=[{'book_order':str(a.pk)} for a in orders])
    if formset.is_valid():
        for form in formset.forms:
            form.save()
        return redirect(reverse('stock_book_orders'))
    return render_to_response('book_stock/deliver_orders.html',
                      {'orders':orders, 'formset':formset},
                      context_instance=RequestContext(request))

def deliver_orders(request):
    orders = BookOrder.objects.filter(pk__in=request.GET.getlist('id'))
    if request.method == 'GET':
        return _deliver_orders_GET(request, orders)
    elif request.method == 'POST':
        return _deliver_orders_POST(request, orders)
