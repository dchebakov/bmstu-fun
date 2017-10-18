from django.contrib import admin

from .models import Task, News, NewTask, Comment, Section

admin.site.register(Task)
admin.site.register(News)
admin.site.register(NewTask)
admin.site.register(Comment)
admin.site.register(Section)