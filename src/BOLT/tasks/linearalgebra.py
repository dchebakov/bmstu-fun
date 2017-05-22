import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re

def comments(request, task):
    is_like = True
    if request.user.is_authenticated():
        is_like = Thanks.objects.filter(task=task,
                                        user=UserProfile.objects.get(user=request.user)).exists()

    return dict({'comments': Comment.objects.filter(task=task),
                 'comment_form': CommentForm(), 'is_like': is_like},
                **views.get_default_data(request))


def task_decorate(function):
    def wrapper(request):
        task = Task.objects.get(function_name=function.__name__)
        solve = function(request)
        return render(request, 'task.html',
                      dict({'template': 'solutions/linearalgebra/' +
                                            function.__name__ + '.html',
                            'task': task, 'solve': solve},
                           **comments(request, task)))

