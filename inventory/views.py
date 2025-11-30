from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Purchase, Category, SaleRecord
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        
        # Stats Cards
        sales_today = SaleRecord.objects.filter(user=user, date_sold__date=today).aggregate(total=Sum('total_price'))['total'] or 0
        all_sales = SaleRecord.objects.filter(user=user)
        total_revenue = all_sales.aggregate(total=Sum('total_price'))['total'] or 0
        total_inventory_value = sum(item.total_value for item in Item.objects.filter(user=user))
        low_stock_count = Item.objects.filter(user=user, quantity__lt=10).count()
        
        context['sales_today'] = sales_today
        context['total_revenue'] = total_revenue
        context['low_stock_count'] = low_stock_count
        context['total_inventory_value'] = total_inventory_value
        context['low_stock_items'] = Item.objects.filter(user=user, quantity__lt=10)

        # Graph Data (Last 30 Days)
        dates = []
        sales_data = []
        for i in range(30):
            d = today - timedelta(days=29-i)
            day_sales = SaleRecord.objects.filter(user=user, date_sold__date=d).aggregate(total=Sum('total_price'))['total'] or 0
            dates.append(d.strftime('%Y-%m-%d'))
            sales_data.append(int(day_sales))
        
        context['graph_dates'] = dates
        context['graph_sales'] = sales_data
        return context

class ProductListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/product_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = Item.objects.filter(user=self.request.user)
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context

class AddProductView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['name', 'category', 'company', 'selling_price', 'quantity', 'average_cost']
    template_name = 'inventory/add_item.html' # Explicitly use the add_item template
    success_url = reverse_lazy('product_list')
    
    def form_valid(self, form):
        # Input Hardening
        try:
            if form.cleaned_data.get('quantity') is not None and form.cleaned_data.get('quantity') < 0:
                form.add_error('quantity', "Quantity must be positive")
                return self.form_invalid(form)
            if form.cleaned_data.get('selling_price') is not None and form.cleaned_data.get('selling_price') < 0:
                form.add_error('selling_price', "Price must be positive")
                return self.form_invalid(form)
        except (ValueError, TypeError):
            return self.form_invalid(form)

        form.instance.user = self.request.user
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Product added successfully!'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)

class AddPurchaseView(LoginRequiredMixin, CreateView):
    model = Purchase
    fields = ['item', 'quantity', 'unit_price']
    template_name = 'inventory/add_purchase.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # The Purchase model's save() method handles updating Item quantity/cost
        return super().form_valid(form)

class SaleView(LoginRequiredMixin, View):
    template_name = 'inventory/sale.html'

    def get(self, request):
        recent_sales = SaleRecord.objects.filter(user=request.user, date_sold__date=timezone.now().date()).order_by('-date_sold')
        return render(request, self.template_name, {'recent_sales': recent_sales})

    def post(self, request):
        product_name = request.POST.get('product_name')
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity <= 0: raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Invalid Quantity: Please enter a whole number greater than 0.")
            return redirect('sales')
        
        with transaction.atomic():
            try:
                item = Item.objects.select_for_update().get(name__iexact=product_name, user=request.user)
            except Item.DoesNotExist:
                messages.error(request, f"Product '{product_name}' not found!")
                return redirect('sales')
            except Item.MultipleObjectsReturned:
                 messages.error(request, f"Multiple products found with name '{product_name}'.")
                 return redirect('sales')

            if item.quantity < quantity:
                messages.error(request, f"Insufficient Stock! Only {item.quantity} available.")
                return redirect('sales')

            total_price = item.selling_price * quantity
            SaleRecord.objects.create(product=item, quantity=quantity, total_price=total_price, user=request.user)
            item.quantity -= quantity
            item.save()
            messages.success(request, f"Sold {quantity} x {item.name} for PKR {total_price}")
            
        return redirect('sales')

def delete_sale(request, pk):
    with transaction.atomic():
        sale = get_object_or_404(SaleRecord, pk=pk, user=request.user)
        item = Item.objects.select_for_update().get(pk=sale.product.pk)
        item.quantity += sale.quantity
        item.save()
        sale.delete()
        messages.success(request, "Sale reversed and stock restored.")
    return redirect('sales')

def export_daily_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="daily_sales.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Product Name', 'Qty Sold', 'Unit Price', 'Total Price'])
    
    sales = SaleRecord.objects.filter(user=request.user, date_sold__date=timezone.now().date())
    for sale in sales:
        writer.writerow([sale.date_sold, sale.product.name, sale.quantity, sale.product.selling_price, sale.total_price])
    return response

def export_monthly_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="monthly_sales.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Product Name', 'Qty Sold', 'Unit Price', 'Total Price'])
    
    today = timezone.now().date()
    sales = SaleRecord.objects.filter(user=request.user, date_sold__month=today.month, date_sold__year=today.year)
    for sale in sales:
        writer.writerow([sale.date_sold, sale.product.name, sale.quantity, sale.product.selling_price, sale.total_price])
    return response

class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'inventory/add_category.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)