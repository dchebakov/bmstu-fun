from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import re
from django.contrib.auth.models import User
from .models import UserProfile, News, Section, Task, Comment, Thanks, NewTask
from .forms import RegistrationForm, SettingsForm, CommentForm, NewTask
import os
from .tasks.probabilitytheory import *
from django.contrib.auth.decorators import login_required

COUNT_POSTS_ON_PAGE = 4
COUNT_TOP_TAGS = 5
COUNT_BEST_MEMBERS = 3


def get_profile(request):
    profile = None
    if request.user.is_authenticated():
        profile = UserProfile.objects.get(user=request.user)
    return profile


# стандартные данные для всех страниц
def get_default_data(request):
    return {'profile': get_profile(request),
            'sections': Section.objects.all(), 'form': login(request),
            'last_comments': Comment.objects.all().order_by('-date_created')[:10]
            }


# фукнция пагинации
def paginate(query_set, request):
    paginator = Paginator(query_set, COUNT_POSTS_ON_PAGE)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return posts


# функция для получения формы авторизации и её обработки
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            if user and user.is_active:
                auth.login(request, form.get_user())
                return redirect(main)
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
    return render(request, 'index.html',
                  dict({'news': paginate(News.objects.get_new(), request)},
                       **get_default_data(request)))


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
    tasks = Task.objects.filter(Q(title__icontains=terms) |
                                Q(title__icontains=terms.lower()))
    if len(tasks) == 0:
        tasks = None
        terms = 'Nothing was found'
    else:
        posts = paginate(tasks, request)

    return render(request, 'search.html', dict({'tasks': tasks,
                                                'title': terms},
                                               **get_default_data(request)))


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


@login_required(login_url=main)
def newtask(request):
    if request.method == 'POST':
        form = NewTask(request.POST, request.FILES)
        if form.is_valid():
            function = form.cleaned_data['function']
            f_path = default_storage.save('tmp/' + function.name, ContentFile(function.read()))

            template = form.cleaned_data['template']
            t_path = default_storage.save('tmp/' + template.name, ContentFile(template.read()))


            return render(request, 'test/testsolution.html', {'templatename'})

    else:
        form = ()
    profile = None
    if request.user.is_authenticated():
        profile = UserProfile.objects.get(user=request.user)

    return render(request, 'test/test.html', {'user': request.user,
                                         'form': form,
                                         'profile': profile,
                                         'sections': Section.objects.all(),
                                         'last_comments': Comment.objects.all().order_by('-date_created')[:5]})
