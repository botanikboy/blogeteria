from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post)
