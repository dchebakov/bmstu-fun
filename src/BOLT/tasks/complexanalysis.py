import math
from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re
from .probabilitytheory import task_decorate


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True

@task_decorate
def complexanalysisEx1(request):
    
    a = request.GET.get('a')
    b = request.GET.get('b')
    
    if not check_args(a, b):
        return {'is_valid': False}

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return {'is_valid': False}
    
    S = a * b
    S = round(S, 3)
    
    solve = {'a': a, 'b': b, 'S': S, 'is_valid': True}
    
    return solve