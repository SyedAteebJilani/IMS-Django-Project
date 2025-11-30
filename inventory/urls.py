from django.urls import path
from .views import (
    CustomLoginView, HomeView, ProductListView, AddProductView, 
    SaleView, export_daily_sales, export_monthly_sales, 
    AddCategoryView, delete_sale, AddPurchaseView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', HomeView.as_view(), name='dashboard'),
    path('home/', HomeView.as_view(), name='home'),
    
    path('products/', ProductListView.as_view(), name='product_list'),
    
    # Fixed: Support both 'add_item' (for dashboard) and 'add_product' (for modal)
    path('products/add/', AddProductView.as_view(), name='add_item'),
    path('products/new/', AddProductView.as_view(), name='add_product'), 
    
    path('products/add-category/', AddCategoryView.as_view(), name='add_category'),
    path('purchase/add/', AddPurchaseView.as_view(), name='add_purchase'),
    
    path('sales/', SaleView.as_view(), name='sales'),
    path('sale/', SaleView.as_view(), name='sale_alias'),
    path('sales/delete/<int:pk>/', delete_sale, name='delete_sale'),
    
    path('export/daily/', export_daily_sales, name='export_daily'),
    path('export/monthly/', export_monthly_sales, name='export_monthly'),
    path('export/', export_daily_sales, name='export_csv'),
]