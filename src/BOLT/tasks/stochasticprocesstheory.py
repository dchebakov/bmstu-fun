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
                if not (0.98 <= sum(row) <= 1.02):
                    return False
                for el in row:
                    if not (0 <= el <= 1):
                        return False
        else:
            if not (0.98 <= sum(lst) <= 1.02):
                return False
            for el in lst:
                if not (0 <= el <= 1):
                    return False
        return True

    def matrix2latex(lst):
        if type(lst[0]) == type(lst):
            return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
                r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))
        else:
            return r'\begin{{pmatrix}} {} \end{{pmatrix}}^T'.format(
                ' & '.join([str(round(el, 2)) for el in lst]))

    ROUNDING_NUMBER = 2
    MAX_STEP = 1000
    ERR = 'Введенные данные не прошли проверку на стохастичность'

    step = request.GET.get('step')
    rows = request.GET.get('rows')
    values = request.GET.get('valuesm')
    valuesv = request.GET.get('valuesv')

    if not check_args(rows, values, valuesv, step) \
            or float(rows) < 1:
        return {'is_valid': False}

    rows = int(rows)
    try:
        step = int(step)
    except ValueError:
        return {'is_valid': False}

    if not 0 <= step <= MAX_STEP:
        ERR = 'Введите другое значение шага'
        return {'err': ERR, 'is_valid': False}

    values = values.split(' ')
    valuesv = valuesv.split(' ')
    values.remove('')

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(rows):
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
    matrix_np = matrix_np.transpose()
    vector_np = np.matrix(vector)
    vector_np = vector_np.transpose()

    answers_in_steps = []
    data = [vector]
    for i in range(step):
        matrix_pow_np = np.linalg.matrix_power(matrix_np, i+1)
        cur_answer = matrix_pow_np * vector_np
        data.append(cur_answer.tolist())
        answers_in_steps.append(matrix2latex(cur_answer.tolist()))

    final = np.linalg.matrix_power(matrix_np, MAX_STEP) * vector_np

    index = [i for i in range(step+1)]
    data = [list(el) for el in zip(*data)]

    return {'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector), 'ans': answers_in_steps, 'step': step,
            'final': matrix2latex(final.tolist()), 'index': index, 'data': data, 'is_valid': True}
