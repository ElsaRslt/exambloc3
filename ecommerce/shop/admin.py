from django.contrib import admin

from .models import Category, Product

#classer les produits et categorie sous forme de tableau avec les informations 
class AdminCategory(admin.ModelAdmin):
    list_display = ('name' , 'date_added')
    
class AdminProduct(admin.ModelAdmin):
    list_display = ('title', 'price','category','date_added')
    
# enregistrement des class models 
admin.site.register(Product, AdminProduct)
admin.site.register(Category, AdminCategory)
