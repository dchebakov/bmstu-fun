from django.conf.urls import url
from .views import main, section, task, changetitle

urlpatterns = [
    url(r'^$', main, name='main'),
    url(r'^section/(?P<section_title>\w+)/$', section, name='section'),
    url(r'^task/(?P<id>\d+)/$', task, name='task'),
    url(r'^changetitle/$', changetitle, name='changetitle'),
]
