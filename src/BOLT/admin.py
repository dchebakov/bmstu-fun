from django.contrib import admin

from .models import Task, News, NewTask

admin.site.register(Task)
admin.site.register(News)
admin.site.register(NewTask)