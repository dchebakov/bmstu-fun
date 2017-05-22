from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
import os
import re
from .models import UserProfile, News, Section, Task, Comment, Thanks, NewTask
from .forms import RegistrationForm, SettingsForm, CommentForm, NewTaskForm
from .tasks.probabilitytheory import *
from .tasks.diffgeometry import *

COUNT_POSTS_ON_PAGE = 4
COUNT_TOP_TAGS = 5
COUNT_BEST_MEMBERS = 3


def get_profile(request):
    profile = None
    if request.user.is_authenticated():
        profile = UserProfile.objects.get(user=request.user)
    return profile


def get_default_data(request):
    '''стандартные данные для всех страниц'''
    return {'profile': get_profile(request),
            'sections': Section.objects.all(), 'form': login(request),
            'last_comments': Comment.objects.all().order_by('-date_created')[:10]
            }


def paginate(query_set, request):
    '''фукнция пагинации'''
    paginator = Paginator(query_set, COUNT_POSTS_ON_PAGE)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return posts


def login(request):
    '''функция для получения формы авторизации и её обработки'''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            if user and user.is_active:
                auth.login(request, form.get_user())
                form = 'login'
    else:
        form = None
        if not request.user.is_authenticated():
            form = AuthenticationForm()
    return form


def section(request, section_title):
    try:
        tasks = Task.objects.filter(section=Section.objects.get(slug=section_title))
    except Task.DoesNotExist:
        tasks = None

    return render(request, 'search.html', dict({'tasks': tasks}, **get_default_data(request)))


def task(request, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        raise Http404

    try:
        return globals()[task.function_name](request)
    except KeyError:
        raise Http404


def main(request):
    default_data = get_default_data(request)
    if default_data['form'] == 'login':
        return redirect(main)
    return render(request, 'index.html',
                  dict({'news': paginate(News.objects.get_new(), request)},
                       **default_data))


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            profile = UserProfile.objects.create(
                user=user,
                avatar=form.cleaned_data['avatar']
            )
            profile.save()
            auth.login(request, profile.user)
            return redirect(main)
    else:
        form = RegistrationForm()

    return render(request, 'signup.html', {'form': form,
                                           'sections': Section.objects.all()})


def logout(request):
    auth.logout(request)
    return redirect(main)


def settings(request):
    if request.user.is_authenticated():
        profile = UserProfile.objects.get(user=request.user)
        if request.method == 'POST':
            form = SettingsForm(request.POST, request.FILES)
            if form.is_valid():
                user = request.user
                if form.cleaned_data['username']:
                    user.username = form.cleaned_data['username']
                if form.cleaned_data['email']:
                    user.email = form.cleaned_data['email']
                if form.cleaned_data['first_name']:
                    user.first_name = form.cleaned_data['first_name']
                user.save()
                profile = UserProfile.objects.get(user=User.objects.get(pk=user.id))
                if form.cleaned_data['avatar']:
                    profile.avatar = form.cleaned_data['avatar']
                profile.save()
                return redirect(settings)
        else:
            form = SettingsForm()
            form.set_default_value(request.user)
        return render(request, 'settings.html', {'user': request.user,
                                                 'form': form,
                                                 'profile': profile,
                                                 'sections': Section.objects.all(),
                                                 'last_comments': Comment.objects.all().order_by('-date_created')[:5]})


def search(request):
    terms = request.GET.get('terms')
    tasks = Task.objects.filter(title__icontains=terms)
    if len(tasks) == 0:
        tasks = None
        terms = 'Nothing was found'
    else:
        posts = paginate(tasks, request)

    default_data = get_default_data(request)
    if default_data['form'] == 'login':
        return redirect(main)

    return render(request, 'search.html', dict({'tasks': tasks,
                                                'title': terms},
                                               **default_data))


def comment(request, id):
    try:
        task = Task.objects.get(pk=id)
    except Task.DoesNotExist:
        return redirect(main)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                user=UserProfile.objects.get(user=request.user),
                text=form.cleaned_data['text'],
                task=Task.objects.get(pk=id)
            )
    return redirect(task)


def thanks(request):
    if request.method == 'POST':
        Thanks.objects.create(
            task=Task.objects.get(pk=request.POST['taskid']),
            user=UserProfile.objects.get(user=request.user)
        ).like()
        task = Task.objects.get(pk=request.POST['taskid'])
        return HttpResponse(json.dumps({'rating': task.rating}), content_type='application/json')

    return redirect(main)


def success(request):
    return render(request, 'success.html',
                  {'success': 'Спасибо! В ближайшее время мы проверим решение и опубликуем его на сайте!',
                   'user': request.user,
                   'profile': get_profile(request),
                   'sections': Section.objects.all(),
                   'last_comments': Comment.objects.all().order_by('-date_created')[:5]})


@login_required(login_url=main)
def newtask(request):
    if request.method == 'POST':
        form = NewTaskForm(request.POST, request.FILES)
        if form.is_valid():
            # function = form.cleaned_data['function']
            # f_path = default_storage.save('tmp/' + function.name, ContentFile(function.read()))
            #
            # template = form.cleaned_data['template']
            # t_path = default_storage.save('tmp/' + template.name, ContentFile(template.read()))

            NewTask.objects.create(
                title=form.cleaned_data['title'],
                function=form.cleaned_data['function'],
                template=form.cleaned_data['template'],
                section=form.cleaned_data['section']
            )
            template = open('/home/chad/BOLT_PROJECT/files/media/' +
                            str(NewTask.objects.get(pk=NewTask.objects.count()).template), 'r')
            text = template.read()
            template.close()
            template = open('/home/chad/BOLT_PROJECT/files/media/' +
                            str(NewTask.objects.get(pk=NewTask.objects.count()).template), 'w')
            template.write(
                '''
                <head>
                    <meta charset="utf-8">
                </head>''' + text)
            template.close()
            print(text)

            return redirect(success)
    else:
        form = NewTaskForm()
        profile = None
        if request.user.is_authenticated():
            profile = UserProfile.objects.get(user=request.user)

    return render(request, 'newtask.html', {'user': request.user,
                                                'form': form,
                                                'profile': get_profile(request),
                                                'sections': Section.objects.all(),
                                                'last_comments': Comment.objects.all().order_by('-date_created')[:5]})


def listofsentsolutions(request):
    if request.user.is_superuser:
        return render(request, 'listofsentsolutions.html', {'user': request.user,
                                                            'profile': get_profile(request),
                                                            'sections': Section.objects.all(),
                                                            'last_comments': Comment.objects.all().order_by(
                                                                '-date_created')[:5],
                                                            'newtasks': NewTask.objects.all()},
                      )
    else:
        return redirect(main)


from django.contrib.admin import ModelAdmin

def checknewsolution(request, id):
    if request.user.is_superuser:
        try:
            newtask = NewTask.objects.get(pk=id)
        except NewTask.DoesNotExist:
            return redirect(listofsentsolutions)
        return render(request, 'checknewsolution.html', {'user': request.user,
                                                         'profile': get_profile(request),
                                                         'sections': Section.objects.all(),
                                                         'last_comments': Comment.objects.all().order_by(
                                                             '-date_created')[:5],
                                                         'newtask': newtask,
                                                         },
                      )
    else:
        return redirect(main)
