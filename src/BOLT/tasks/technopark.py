import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re

def exchange_3(sum, count, monets):
    if sum < 0:
        return count
    elif sum == 0:
        return count + 1
    count += exchange_2(sum, 0, monets[1::])
    sum -= monets[0]
    return exchange_3(sum, count, monets)

def exchange_2(sum, count, monets):
    if sum < 0:
        return count
    elif sum == 0:
        return count + 1
    if sum % monets[1] == 0:
        count += 1
    return exchange_2(sum - monets[0], count, monets)

def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True

def isint(s):
    '''Проверка на int'''
    try:
        int(s)
        return True
    except ValueError:
        return False

@task_decorate
def technoparkEx1(request):

    sum = request.GET.get('sum')
    monets_input = request.GET.get('monets')

    if not check_args(sum, monets_input):
        return {'is_valid': False}
    if not isint(sum):
        return {'is_valid': False}

    try:
        monets = [int(v) for v in filter(None, re.split("[, ]+", monets_input))]
    except ValueError:
        return {'is_valid': False}

    sum = int(sum)
    if sum > 500:
        return {'is_valid': False}

    if len(monets) == 2:
        answer = exchange_2(sum, 0, monets)
    elif len(monets) == 1:
        answer = 1
    elif len(monets) == 3:
        answer = exchange_3(sum, 0, monets)
    else:
        return {'is_valid': False}
    solve = {'answer': answer, 'sum': sum, 'monets': monets, 'is_valid': True}
    return solve
