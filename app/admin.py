from django.contrib import admin

from .models import *
from django.contrib import admin

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.register(Post)
class ProductAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]

admin.site.register(PostImage)


admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Notifications)


admin.site.register(SearchHistory)

# Register your models here.
