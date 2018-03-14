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

ROUNDING_NUMBER = 2


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


def matrix2latex(lst):
    if type(lst[0]) == type(lst):
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
            r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))
    else:
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}^T'.format(
            ' & '.join([str(round(el, 2)) for el in lst]))


@task_decorate
def stochasticprocesstheoryEx1(request):
    def stochastic_validity(lst):
        if type(lst[0]) == type(lst):
            for row in lst:
                if sum(row) != 1:
                    return False
                for el in row:
                    if not (0 <= el <= 1):
                        return False
        else:
            if sum(lst) != 1:
                return False
            for el in lst:
                if not (0 <= el <= 1):
                    return False
        return True

    MAX_STEP = 500
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
        matrix_pow_np = np.linalg.matrix_power(matrix_np, i + 1)
        cur_answer = matrix_pow_np * vector_np
        data.append(cur_answer.tolist())
        answers_in_steps.append(matrix2latex(cur_answer.tolist()))

    final = np.linalg.matrix_power(matrix_np, MAX_STEP) * vector_np

    index = [i for i in range(step + 1)]
    data = [list(el) for el in zip(*data)]

    return {'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector), 'ans': answers_in_steps, 'step': step,
            'final': matrix2latex(final.tolist()), 'index': index, 'data': data, 'is_valid': True}


@task_decorate
def stochasticprocesstheoryEx2(request):
    NUMBER_OF_NODES = request.GET.get('nn');
    NUMBER_OF_EDGES = request.GET.get('ne');
    edges = request.GET.get('edg');

    if not check_args(NUMBER_OF_NODES, NUMBER_OF_EDGES, edges):
        return {'is_valid': False}

    try:
        edges = [float(s) for s in edges.split()]
        NUMBER_OF_NODES = int(NUMBER_OF_NODES)
        NUMBER_OF_EDGES = int(NUMBER_OF_EDGES)
    except ValueError:
        return {'is_valid': False}

    if len(edges) % 3 != 0 or len(edges) / 3 != float(NUMBER_OF_EDGES):
        return {'is_valid': False}

    edges = [list(el) for el in zip(*[iter(edges)] * 3)]

    H = np.zeros((NUMBER_OF_NODES, NUMBER_OF_NODES))

    for node in range(1, NUMBER_OF_NODES + 1):
        for edge in edges:
            if edge[0] == node:
                H[node - 1][node - 1] -= edge[2]
            if edge[1] == node:
                H[node - 1][int(edge[0] - 1)] += edge[2]

    return {'H': matrix2latex(H.tolist()), 'is_valid': True}
