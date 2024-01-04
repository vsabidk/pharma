from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from more_itertools import quantify  # Unused import
from .models import *  # Importing all models from the current directory's models.py
from datetime import datetime

# Form for saving Product information
class SaveProduct(forms.ModelForm):
    # Defining form fields with specific validations and properties
    name = forms.CharField(max_length="250")
    description = forms.Textarea()
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')])
    description = forms.CharField(max_length=250)  # Note: 'description' field defined twice - possibly an error

    class Meta:
        model = Product
        fields = ('code', 'name', 'description', 'status', 'price')

    # Custom validation for ensuring unique product code
    def clean_code(self):
        id = self.instance.id if self.instance.id else 0
        code = self.cleaned_data['code']
        try:
            if int(id) > 0:
                product = Product.objects.exclude(id=id).get(code=code)
            else:
                product = Product.objects.get(code=code)
        except:
            return code
        raise forms.ValidationError(f"{code} Category Already Exists.")

# Form for saving Stock information
class SaveStock(forms.ModelForm):
    # Defining form fields with specific validations and properties
    product = forms.CharField(max_length=30)
    quantity = forms.CharField(max_length=250)
    type = forms.ChoiceField(choices=[('1', 'Stock-in'), ('2', 'Stock-Out')])

    class Meta:
        model = Stock
        fields = ('product', 'quantity', 'type')

    # Custom validation for checking valid product
    def clean_product(self):
        pid = self.cleaned_data['product']
        try:
            product = Product.objects.get(id=pid)
            return product
        except:
            raise forms.ValidationError("Product is not valid")

# Form for saving Invoice information
class SaveInvoice(forms.ModelForm):
    # Defining form fields with specific validations and properties
    transaction = forms.CharField(max_length=100)
    customer = forms.CharField(max_length=250)
    total = forms.FloatField()

    class Meta:
        model = Invoice
        fields = ('transaction', 'customer', 'total')

    # Custom validation for generating a unique transaction ID based on date
    def clean_transaction(self):
        pref = datetime.today().strftime('%Y%m%d')
        transaction = ''
        code = str(1).zfill(4)
        while True:
            invoice = Invoice.objects.filter(transaction=str(pref + code)).count()
            if invoice > 0:
                code = str(int(code) + 1).zfill(4)
            else:
                transaction = str(pref + code)
                break
        return transaction

# Form for saving Invoice_Item information
class SaveInvoiceItem(forms.ModelForm):
    # Defining form fields with specific validations and properties
    invoice = forms.CharField(max_length=30)
    product = forms.CharField(max_length=30)
    quantity = forms.CharField(max_length=100)
    price = forms.CharField(max_length=100)

    class Meta:
        model = Invoice_Item
        fields = ('invoice', 'product', 'quantity', 'price')

    # Custom validation for checking valid invoice ID
    def clean_invoice(self):
        iid = self.cleaned_data['invoice']
        try:
            invoice = Invoice.objects.get(id=iid)
            return invoice
        except:
            raise forms.ValidationError("Invoice ID is not valid")

    # Custom validation for checking valid product
    def clean_product(self):
        pid = self.cleaned_data['product']
        try:
            product = Product.objects.get(id=pid)
            return product
        except:
            raise forms.ValidationError("Product is not valid")

    # Custom validation for checking valid quantity
    def clean_quantity(self):
        qty = self.cleaned_data['quantity']
        if qty.isnumeric():
            return int(qty)
        raise forms.ValidationError("Quantity is not valid")
