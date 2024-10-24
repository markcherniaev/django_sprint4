from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'location', 'pub_date',
                    'is_published')
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'category', 'location')
    date_hierarchy = 'pub_date'
    raw_id_fields = ('author',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
