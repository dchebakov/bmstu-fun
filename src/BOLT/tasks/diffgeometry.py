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
                      dict({'template': 'solutions/diffgeometry/' +
                                            function.__name__ + '.html',
                            'task': task, 'solve': solve},
                           **comments(request, task)))

    return wrapper

def check_args(*args): # Общая проверка
    for arg in args:
        if not arg:
            return False
    return True    

@task_decorate
def diffgeometryEx1(request):
    
    xi1 = request.GET.get('xi1')
    xi2 = request.GET.get('xi2')
    eta1 = request.GET.get('eta1')
    eta2 = request.GET.get('eta2')
    
    if not check_args(xi1, xi2, eta1, eta2):
        return {'is_valid': False}

    xi11 = re.sub(r'\^', '**', str(xi1))
    xi22 = re.sub(r'\^', '**', str(xi2))
    eta11 = re.sub(r'\^', '**', str(eta1))
    eta22 = re.sub(r'\^', '**', str(eta2))
    x = [Symbol('x'), Symbol('y')]
    
    xi = [parse_expr(xi11), parse_expr(xi22)]
    eta = [parse_expr(eta11), parse_expr(eta22)]
    
    phi = [0, 0]
    for i in range(2):
        for a in range(2):           
            phi[i] += (xi[a]*diff(eta[i], x[a]) - eta[a]*diff(xi[i], x[a]))
        phi[i] = latex(phi[i])
    
    
    solve = {'phi1':  phi[0], 'phi2': phi[1], 'xi1': xi1, 'xi2': xi2, 'eta1': eta1, 'eta2': eta2, 'is_valid': True}
    
    return solve