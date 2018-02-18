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
    ROUNDING_NUMBER = 2

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

    cheb_norm = round(max(sum(row) for row in matrix), ROUNDING_NUMBER)

    def matrix2latex(lst):
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
            r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))

    def chebnorm2latex(lst):
        return r'\left | {} \right |'.format(
            r'\right | , \left |'.join(
                [(str.join(' + ', (str(round(el, ROUNDING_NUMBER)) + 'x^' + str(row.index(el) + 1) for el in row))) for
                 row in lst]))

    return {'rows': rows, 'columns': columns, 'matrix': matrix2latex(matrix), 'cheb': chebnorm2latex(matrix),
            'cheb_norm': cheb_norm, 'is_valid': True}
