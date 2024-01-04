from email import message
from unicodedata import category
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from ims_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from imsApp.forms import *
from imsApp.models import *
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from django.shortcuts import render
from django.db.models import Q
# A dictionary called 'context' is created to hold data that will be sent to HTML templates.
context = {
    'page_title': 'File Management System',  # Initial page title set to 'File Management System'.
}

# This function handles the homepage of the web application.
def home(request):
    # Changes the 'page_title' in the 'context' dictionary to 'Home'.
    context['page_title'] = 'Home'
    # Renders the 'home.html' template file, passing the 'context' data to it.
    return render(request, 'home.html', context)

# Manages the product section of the application.
def product_mgt(request):
    # Changes the 'page_title' in the 'context' dictionary to 'Product List'.
    context['page_title'] = "Product List"
    # Retrieves all products from the database using the Product model.
    products = Product.objects.all()
    # Adds the retrieved products to the 'context' dictionary.
    context['products'] = products
    # Renders the 'product_mgt.html' template file, passing the 'context' data to it.
    return render(request, 'product_mgt.html', context)

# Saves product data either as a new entry or updates an existing one.
def save_product(request):
    # Initializes a response dictionary with default values for indicating success or failure.
    resp = {'status': 'failed', 'msg': ''}
    
    # Checks if the incoming request method is POST (typically used for form submissions).
    if request.method == 'POST':
        # Checks if the 'id' sent through the POST request is a number.
        if (request.POST['id']).isnumeric():
            # Retrieves an existing product from the database based on the provided ID.
            product = Product.objects.get(pk=request.POST['id'])
        else:
            # If 'id' is not a number or doesn't exist, sets product to None.
            product = None
        
        # Creates a form instance either for a new product or for updating an existing one.
        if product is None:
            form = SaveProduct(request.POST)
        else:
            form = SaveProduct(request.POST, instance=product)
        
        # Checks if the form data is valid.
        if form.is_valid():
            # Saves the form data to the database.
            form.save()
            # Sets a success message for the user.
            messages.success(request, 'Product has been saved successfully.')
            resp['status'] = 'success'  # Updates response status to success.
        else:
            # If form data is invalid, collects and formats error messages.
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'  # Sets an error message if no data was sent with the request.
    
    # Returns a JSON response with the status of the operation and any associated messages.
    return HttpResponse(json.dumps(resp), content_type='application/json')

# Manages individual product information for viewing or editing.
def manage_product(request, pk=None):
    # Changes the 'page_title' in the 'context' dictionary to 'Manage Product'.
    context['page_title'] = "Manage Product"
    
    # Checks if a product ID (pk) is provided.
    if not pk is None:
        # Retrieves a product from the database using the provided ID.
        product = Product.objects.get(id=pk)
        # Adds the retrieved product to the 'context' dictionary.
        context['product'] = product
    else:
        # Sets an empty dictionary for 'product' in the 'context' if no ID is provided.
        context['product'] = {}
    
    # Renders the 'manage_product.html' template file, passing the 'context' data to it.
    return render(request, 'manage_product.html', context)

# Deletes a product from the database.
def delete_product(request):
    # Initializes a response dictionary with default values for indicating success or failure.
    resp = {'status': 'failed', 'msg': ''}
    
    # Checks if the incoming request method is POST (typically used for form submissions).
    if request.method == 'POST':
        try:
            # Retrieves a product from the database based on the provided ID in the POST request.
            product = Product.objects.get(id=request.POST['id'])
            # Deletes the retrieved product.
            product.delete()
            # Sets a success message for the user.
            messages.success(request, 'Product has been deleted successfully')
            resp['status'] = 'success'  # Updates response status to success.
        except Exception as err:
            resp['msg'] = 'Product has failed to delete'  # Sets an error message on failure.
            print(err)  # Prints the error to console for debugging purposes.
    else:
        resp['msg'] = 'Product has failed to delete'  # Sets an error message for non-POST requests.
    
    # Returns a JSON response with the status of the operation and any associated messages.
    return HttpResponse(json.dumps(resp), content_type="application/json")


#Inventory

# Inventory view function
def inventory(request):
    context['page_title'] = 'Inventory'  # Setting page title
    products = Product.objects.all()  # Retrieving all products from the database
    context['products'] = products  # Adding products to the context
    return render(request, 'inventory.html', context)  # Rendering 'inventory.html' with the context

# Inventory History view function
def inv_history(request, pk=None):
    context['page_title'] = 'Inventory History'  # Setting page title
    if pk is None:
        messages.error(request, "Product ID is not recognized")  # Handling case when product ID is missing
        return redirect('inventory-page')  # Redirecting to the inventory page
    else:
        product = Product.objects.get(id=pk)  # Retrieving product with given ID
        stocks = Stock.objects.filter(product=product).all()  # Retrieving stock history related to the product
        context['product'] = product  # Adding product to the context
        context['stocks'] = stocks  # Adding stock history to the context
        return render(request, 'inventory-history.html', context)  # Rendering 'inventory-history.html' with the context

# Stock Form view function
def manage_stock(request, pid=None, pk=None):
    if pid is None:
        messages.error(request, "Product ID is not recognized")  # Handling case when product ID is missing
        return redirect('inventory-page')  # Redirecting to the inventory page
    context['pid'] = pid  # Adding product ID to the context
    if pk is None:
        context['page_title'] = "Add New Stock"  # Setting page title for adding new stock
        context['stock'] = {}  # Initializing empty stock data in the context
    else:
        context['page_title'] = "Manage New Stock"  # Setting page title for managing stock
        stock = Stock.objects.get(id=pk)  # Retrieving stock with given ID
        context['stock'] = stock  # Adding stock data to the context
    return render(request, 'manage_stock.html', context)  # Rendering 'manage_stock.html' with the context

# Save Stock view function
def save_stock(request):
    resp = {'status': 'failed', 'msg': ''}  # Initializing response dictionary
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            stock = Stock.objects.get(pk=request.POST['id'])  # Retrieving stock with given ID
        else:
            stock = None
        if stock is None:
            form = SaveStock(request.POST)  # Creating a form instance for new stock
        else:
            form = SaveStock(request.POST, instance=stock)  # Creating a form instance for existing stock
        if form.is_valid():
            form.save()  # Saving the form data
            messages.success(request, 'Stock has been saved successfully.')  # Displaying success message
            resp['status'] = 'success'  # Updating response status
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")  # Adding error messages to response
    else:
        resp['msg'] = 'No data has been sent.'  # Setting response message for non-POST requests
    return HttpResponse(json.dumps(resp), content_type='application/json')  # Returning response as JSON

# Delete Stock view function
def delete_stock(request):
    resp = {'status': 'failed', 'msg': ''}  # Initializing response dictionary
    if request.method == 'POST':
        try:
            stock = Stock.objects.get(id=request.POST['id'])  # Retrieving stock with given ID
            stock.delete()  # Deleting the stock
            messages.success(request, 'Stock has been deleted successfully')  # Displaying success message
            resp['status'] = 'success'  # Updating response status
        except Exception as err:
            resp['msg'] = 'Stock has failed to delete'  # Handling deletion failure
            print(err)
    else:
        resp['msg'] = 'Stock has failed to delete'  # Handling case when request method is not POST
    return HttpResponse(json.dumps(resp), content_type="application/json")  # Returning response as JSON


# Sales Management view function
def sales_mgt(request):
    context['page_title'] = 'Sales'  # Setting page title
    products = Product.objects.filter(status=1).all()  # Retrieving products with status=1 from the database
    context['products'] = products  # Adding products to the context
    return render(request, 'sales.html', context)  # Rendering 'sales.html' with the context

# Get Product view function
def get_product(request, pk=None):
    resp = {'status': 'failed', 'data': {}, 'msg': ''}  # Initializing response dictionary
    if pk is None:
        resp['msg'] = 'Product ID is not recognized'  # Handling case when product ID is missing
    else:
        product = Product.objects.get(id=pk)  # Retrieving product with given ID
        # Adding product details to the response data
        resp['data']['product'] = str(product.code + " - " + product.name)
        resp['data']['id'] = product.id
        resp['data']['price'] = product.price
        resp['status'] = 'success'  # Updating response status for successful retrieval
    return HttpResponse(json.dumps(resp), content_type="application/json")  # Returning response as JSON

# Save Sales view function
def save_sales(request):
    resp = {'status': 'failed', 'msg': ''}  # Initializing response dictionary
    id = 2  # Initializing id variable with a value of 2 (This might be used later)
    if request.method == 'POST':
        pids = request.POST.getlist('pid[]')  # Retrieving a list of product IDs from the POST data
        invoice_form = SaveInvoice(request.POST)  # Creating an instance of SaveInvoice form
        if invoice_form.is_valid():
            invoice_form.save()  # Saving the invoice data
            invoice = Invoice.objects.last()  # Retrieving the last created invoice
            for pid in pids:
                data = {
                    'invoice': invoice.id,
                    'product': pid,
                    'quantity': request.POST['quantity[' + str(pid) + ']'],  # Retrieving quantity for a specific product
                    'price': request.POST['price[' + str(pid) + ']'],  # Retrieving price for a specific product
                }
                ii_form = SaveInvoiceItem(data=data)  # Creating an instance of SaveInvoiceItem form with data
                if ii_form.is_valid():
                    ii_form.save()  # Saving the invoice item data
                else:
                    # Handling errors if the form is not valid
                    for fields in ii_form:
                        for error in fields.errors:
                            resp['msg'] += str(error + "<br>")  # Adding error messages to the response
                    break  # Breaking the loop if there are errors
            messages.success(request, "Sale Transaction has been saved.")  # Displaying success message
            resp['status'] = 'success'  # Updating response status for successful transaction
        else:
            # Handling errors in the invoice form if it's not valid
            for fields in invoice_form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")  # Adding error messages to the response
    return HttpResponse(json.dumps(resp), content_type="application/json")  # Returning response as JSON

# View function to display a list of all invoices
def invoice_list(request):
    context['page_title'] = 'Invoices'  # Setting the page title
    invoices = Invoice.objects.all()  # Retrieving all invoices from the database
    return render(request, 'invoice_list.html', {'invoices': invoices})  # Rendering 'invoice_list.html' with invoices in the context

# View function to display a filtered list of invoices based on query parameters
def filtered_invoice_list(request):
    # Retrieving query parameters from the request URL
    query_customer = request.GET.get('customer')
    query_date = request.GET.get('date')
    query_invoice_id = request.GET.get('invoice_id')

    invoices = Invoice.objects.all()  # Retrieving all invoices initially

    # Filtering invoices based on query parameters, if provided
    if query_customer:
        invoices = invoices.filter(customer__icontains=query_customer)  # Filtering by customer name

    if query_date:
        invoices = invoices.filter(date_created__date=query_date)  # Filtering by invoice creation date

    if query_invoice_id:
        invoices = invoices.filter(transaction__icontains=query_invoice_id)  # Filtering by invoice transaction ID

    return render(request, 'invoice_list.html', {'invoices': invoices})  # Rendering 'invoice_list.html' with filtered invoices in the context
