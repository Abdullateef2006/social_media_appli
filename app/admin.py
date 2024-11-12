from django.contrib import admin

from .models import *


admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Notification)


admin.site.register(Post)
admin.site.register(SearchHistory)

# Register your models here.
