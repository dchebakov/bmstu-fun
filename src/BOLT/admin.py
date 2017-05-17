from django.contrib import admin

from .models import Task, News

admin.site.register(Task)
admin.site.register(News)
# Register your models here.
