from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.shortcuts import render, redirect
from .models import Section, Task
from .tasks.solutions import *
from .forms import ChangeTitleForm


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


def changetitle(request):
    if request.method == 'POST':
        form = ChangeTitleForm(request.POST)
        if form.is_valid():
            task = Task.objects.get(pk=1)
            task.title = form.cleaned_data['title']
            task.save()
            return redirect(section, section_title='solutions')
    else:
        form = ChangeTitleForm()
    return render(request, 'changetitle.html', {'form': form['title'], 'sections': Section.objects.all()})
