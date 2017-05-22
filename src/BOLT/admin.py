from django.contrib import admin

from .models import Task, News, NewTask, Comment

admin.site.register(Task)
admin.site.register(News)
admin.site.register(NewTask)
admin.site.register(Comment)
