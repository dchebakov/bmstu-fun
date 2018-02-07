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


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


@task_decorate
def functionalanalysisEx1(request):
    rows = request.GET.get('rows')
    columns = request.GET.get('columns')
    values = request.GET.get('values')

    if not check_args(rows, columns, values) \
            or float(rows) <= 1 \
            or float(columns) <= 1:
        return {'is_valid': False}

    rows = int(rows)
    columns = int(columns)
    values = values.split(' ')

    if len(values) != rows * columns:
        return {'is_valid': False}

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(columns):
            row.append(float(values.pop(0)))
        matrix.append(row)

    solve = {'rows': rows, 'columns': columns, 'matrix': matrix, 'is_valid': True}

    return solve
