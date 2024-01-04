from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

urlpatterns = [
    # Redirect to the admin page from a custom URL
    path('redirect-admin', RedirectView.as_view(url="/admin"), name="redirect-admin"),

    # Various URL patterns mapped to their respective views
    path('', views.home, name='home-page'),  # Homepage
    path('product', views.product_mgt, name='product-page'),  # Product management page
    path('manage_product', views.manage_product, name='manage-product'),  # Manage product
    path('save_product', views.save_product, name='save-product'),  # Save product
    path('manage_product/<int:pk>', views.manage_product, name='manage-product-pk'),  # Manage product with a specific ID
    path('delete_product', views.delete_product, name='delete-product'),  # Delete product
    path('inventory', views.inventory, name='inventory-page'),  # Inventory page
    path('inventory/<int:pk>', views.inv_history, name='inventory-history-page'),  # Inventory history for a product
    path('stock/<int:pid>', views.manage_stock, name='manage-stock'),  # Manage stock for a product
    path('stock/<int:pid>/<int:pk>', views.manage_stock, name='manage-stock-pk'),  # Manage stock with a specific ID
    path('save_stock', views.save_stock, name='save-stock'),  # Save stock
    path('delete_stock', views.delete_stock, name='delete-stock'),  # Delete stock
    path('sales', views.sales_mgt, name='sales-page'),  # Sales management page
    path('get_product', views.get_product, name='get-product'),  # Get product information
    path('get_product/<int:pk>', views.get_product),  # Get product information with a specific ID
    path('save_sales', views.save_sales, name="save-sales"),  # Save sales transaction
    path('invoices/', views.invoice_list, name='invoice-list'),  # List of invoices
    path('invoices/filter/', views.filtered_invoice_list, name='filtered-invoice-list'),  # Filtered list of invoices
]
