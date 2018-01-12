from django.shortcuts import render, redirect, get_object_or_404
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
from django.conf import settings as st
import json
import os
import re
import shutil
import scipy.stats as ss
from .models import UserProfile, News, Section, Task, Comment, Thanks, NewTask
from .forms import RegistrationForm, SettingsForm, CommentForm, NewTaskForm, SectionForm, NewTaskModelForm

from BOLT.tasks.diffgeometry import *
from BOLT.tasks.analyticgeometry import *
from BOLT.tasks.diffequation import *
from BOLT.tasks.functionalanalysis import *
from BOLT.tasks.linearalgebra import *
from BOLT.tasks.mathanalysis import *
from BOLT.tasks.complexanalysis import *
from BOLT.tasks.probabilitytheory import *
from BOLT.tasks.mathstatistics import *
from BOLT.tasks.technopark import *

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
        task = Task.objects.get(pk=int(id))
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
    if request.user.is_authenticated():
        return redirect(settings)
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
            NewTask.objects.create(
                title=form.cleaned_data['title'],
                function=form.cleaned_data['function'],
                template=form.cleaned_data['template'],
                section=form.cleaned_data['section']
            )
            template = open('/home/chad/BOLT_PROJECT/files/media/' +
                            str(NewTask.objects.last().template), 'r')
            text = template.read()
            template.close()
            template = open('/home/chad/BOLT_PROJECT/files/media/' +
                            str(NewTask.objects.last().template), 'w')
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


@login_required(login_url=main)
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


def checknewsolution(request, id):
    if not request.user.is_superuser:
        return redirect(main)

    if 'delete' in request.POST:
        newtask = NewTask.objects.get(pk=id)
        os.remove(os.path.join(st.MEDIA_ROOT, *re.split(r'/', str(newtask.function))))
        os.remove(os.path.join(st.MEDIA_ROOT, *re.split(r'/', str(newtask.template))))
        newtask.delete()
        return redirect(listofsentsolutions)

    newtask = get_object_or_404(NewTask, id=id)
    formset = NewTaskModelForm(request.POST or None, request.FILES or None, instance=newtask)

    newtask_function = newtask.function
    newtask_template = newtask.template

    if formset.is_valid() and 'save' in request.POST:
        formset.save(commit=False)
        function = formset.cleaned_data['function'].read().decode()
        function = re.sub(r'solution', str(formset.cleaned_data['section']) +
                          'Ex' + str(formset.cleaned_data['exercise_number']), function)

        template = formset.cleaned_data['template'].read().decode()

        with open(os.path.join(st.BASE_DIR, 'templates', 'solutions',
                               str(formset.cleaned_data['section']),
                               str(formset.cleaned_data['section']) + 'Ex' +
                               str(formset.cleaned_data['exercise_number']) + r'.html'), 'w') as template_file:
            template_file.write(template)

        with open(os.path.join(st.BASE_DIR, 'BOLT', 'tasks',
                               str(formset.cleaned_data['section']) + r'.py'), 'a') as function_file:
            function_file.write('\n\n' + r'@task_decorate' +
                                '\n' + function)

        os.remove(os.path.join(st.MEDIA_ROOT, *re.split(r'/', str(newtask_function))))
        os.remove(os.path.join(st.MEDIA_ROOT, *re.split(r'/', str(newtask_template))))
        newtask.delete()

        Task.objects.create(
            title=formset.cleaned_data['title'],
            section=Section.objects.get(slug=formset.cleaned_data['section']),
            function_name=str(formset.cleaned_data['section']) + 'Ex' + str(formset.cleaned_data['exercise_number'])
        )

        return redirect(listofsentsolutions)

    return render(request, 'checknewsolution.html', {'formset': formset,
                                                     'user': request.user,
                                                     'profile': get_profile(request),
                                                     'sections': Section.objects.all(),
                                                     'last_comments': Comment.objects.all().order_by(
                                                         '-date_created')[:5],
                                                     'newtask': newtask,
                                                     })


def aboutus(request):
    if request.method == 'GET':
        return render(request, 'aboutus.html', get_default_data(request))
    else:
        content = json.loads(request.body.decode('utf-8'))
        case = content['case']
        if case == 'quantile':
            dist_type = content['type']
            freedom1 = float(content['freedom1'])
            freedom2 = float(content['freedom2'])
            level = float(content['level'])

            res = 'err'

            if dist_type == 'norm':
                res = ss.norm.ppf(level)
            elif dist_type == 't':
                res = ss.t.ppf(level, freedom1)
            elif dist_type == 'exp':
                res = ss.expon.ppf(level, freedom1)
            elif dist_type == 'chi2':
                res = ss.chi2.ppf(level, freedom1)
            elif dist_type == 'f':
                res = ss.f.ppf(level, freedom1, freedom2)

        elif case == 'laplace':
            pass


        return HttpResponse(res, content_type='application/json')


def utility(request):
    return render(request, 'utility.html', get_default_data(request))


def test(request, id):
    instance = get_object_or_404(NewTask, id=id)
    form = NewTaskModelForm(request.POST or None, instance=instance)
    if form.is_valid():
        return redirect(test, id=25)
    return render(request, 'test/test.html', {'formset': form})
