from django.contrib import admin

from .models import Category, Advert, Response

# Register your models here.
admin.site.register(Category)
admin.site.register(Advert)
admin.site.register(Response)
