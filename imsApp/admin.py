from django.contrib import admin
from imsApp.models import *  # Importing all models from imsApp.models

# Registering models to make them accessible in the Django admin panel
admin.site.register(Product)  # Registering the Product model
admin.site.register(Stock)  # Registering the Stock model
admin.site.register(Invoice)  # Registering the Invoice model
admin.site.register(Invoice_Item)  # Registering the Invoice_Item model
