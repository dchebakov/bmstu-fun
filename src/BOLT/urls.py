from django.conf.urls import url
from .views import (main, search, signup, logout,
                    settings, section, task, comment,
                    thanks, newtask, success, listofsentsolutions,
                    checknewsolution, about_us, utility, test)

urlpatterns = [
    url(r'^$', main, name='main'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^settings/$', settings, name='settings'),
    url(r'^search/$', search, name='search'),
    url(r'^section/(?P<section_title>\w+)/$', section, name='section'),
    url(r'^task/(?P<id>\d+)/$', task, name='task'),
    url(r'^comment/(?P<id>\d+)/$', comment, name='comment'),
    url(r'^thanks/$', thanks, name='thanks'),
    url(r'^newtask/$', newtask, name='newtask'),
    url(r'^success/$', success, name='success'),
    url(r'^listofsentsolutions/$', listofsentsolutions, name='listofsentsolutions'),
    url(r'^checknewsolution/(?P<id>\d+)$', checknewsolution, name='checknewsolution'),
    # url(r'^createnewtask/(?P<id>\d+)$', createnewtask, name='createnewtask'),
    # url(r'^deletetask/(?P<id>\d+)$', deletetask, name='deletetask'),
    url(r'^aboutus/', about_us, name='aboutus'),
    url(r'^utility/', utility, name='utility'),
    url(r'^test/', test, name='test')
    # url(r'^rate/$',rate,name='rate')
]
