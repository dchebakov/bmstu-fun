import math
from bisect import bisect, bisect_left
from scipy.stats import chi2, norm, t
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import numpy as np
from sympy.parsing.sympy_parser import parse_expr
import re
import json


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


@task_decorate
def stochasticprocesstheoryEx1(request):
    def stochastic_validity(lst):
        if type(lst[0]) == type(lst):
            for row in lst:
                if sum(row) != 1:
                    return False
                for el in row:
                    if el > 1 or el < 0:
                        return False
        else:
            if sum(lst) != 1:
                return False
            for el in lst:
                if el > 1 or el < 0:
                    return False
        return True

    ROUNDING_NUMBER = 2
    ERR = 'Введенные данные не прошли проверку на стохастичность'

    step = request.GET.get('step')
    rows = request.GET.get('rows')
    columns = request.GET.get('columns')
    values = request.GET.get('valuesm')
    valuesv = request.GET.get('valuesv')

    if not check_args(rows, columns, values, valuesv, step) \
            or float(rows) <= 1 \
            or float(columns) <= 1 \
            or float(step) < 0:
        return {'is_valid': False}

    rows = int(rows)
    columns = int(columns)
    try:
        step = int(step)
    except ValueError:
        return {'is_valid': False}
    values = values.split(' ')
    valuesv = valuesv.split(' ')
    values.remove('')

    if len(values) != rows * columns:
        return {'is_valid': False}

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(columns):
            try:
                row.append(float(values.pop(0)))
            except ValueError:
                return {'is_valid': False}
        matrix.append(row)

    if not stochastic_validity(matrix):
        return {'err': ERR, 'is_valid': False}

    vector = []
    for _ in range(rows):
        try:
            vector.append(float(valuesv.pop(0)))
        except ValueError:
            return {'is_valid': False}

    if not stochastic_validity(vector):
        return {'err': ERR, 'is_valid': False}

    matrix_np = np.matrix(matrix)
    matrix_np = np.linalg.matrix_power(matrix_np, step)
    matrix_np = matrix_np.transpose()
    vector_np = np.matrix(vector)
    vector_np = vector_np.transpose()
    ans = matrix_np * vector_np
    ans = ans.tolist()

    def matrix2latex(lst):
        if type(lst[0]) == type(lst):
            return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
                r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))
        else:
            return r'\begin{{pmatrix}} {} \end{{pmatrix}}^T'.format(
                ' & '.join([str(round(el, 2)) for el in lst]))

    return {'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector), 'ans': matrix2latex(ans), 'step': step,
            'is_valid': True}
