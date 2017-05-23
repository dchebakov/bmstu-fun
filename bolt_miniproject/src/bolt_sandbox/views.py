# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.shortcuts import render
from .models import Section, Task
from .tasks.solutions import *
# Create your views here.

def main(request):
    return render(request, 'index.html', {'sections': Section.objects.all()})

def section(request, section_title):
    try:
        tasks = Task.objects.filter(section=Section.objects.get(slug=section_title))
    except Task.DoesNotExist:
        tasks = None

    return render(request, 'search.html', {'tasks': tasks, 'sections': Section.objects.all()})

def task(request, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        raise Http404

    try:
        return globals()[task.function_name](request)
    except KeyError:
        raise Http404