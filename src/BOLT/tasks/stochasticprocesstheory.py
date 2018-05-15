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
from sympy import Symbol, Function, latex, solve
from sympy import *
from scipy.integrate import odeint
from sympy.parsing.sympy_parser import parse_expr
import re
import json
import os

ROUNDING_NUMBER = 2
ERR = 'Введенные данные не прошли проверку на стохастичность'


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


def round_list(lst):
    return list(map(lambda x: round(x, ROUNDING_NUMBER + 3), lst))


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


@task_decorate
def stochasticprocesstheoryEx1(request):
    MAX_STEP = 500

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
        return {'err': 'Введите другое значение шага', 'is_valid': False}

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
        cur_answer = list(map(float, matrix_pow_np * vector_np))
        data.append(cur_answer)
        answers_in_steps.append(matrix2latex(cur_answer))

    final = np.linalg.matrix_power(matrix_np, MAX_STEP) * vector_np
    index = [i for i in range(step + 1)]
    data = [round_list(list(el)) for el in zip(*data)]

    return {'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector), 'ans': answers_in_steps, 'step': step,
            'final': matrix2latex(final.tolist()), 'index': index, 'data': data, 'is_valid': True}


@task_decorate
def stochasticprocesstheoryEx2(request):
    TIME_MAX = 100  # max time value for solving ODE
    TIME_STEP = 0.2
    TIME_GRAPH = 5  # max time value for plotting

    NUMBER_OF_NODES = request.GET.get('nn')
    NUMBER_OF_EDGES = request.GET.get('ne')
    edges = request.GET.get('edg')
    values = request.GET.get('values')

    if not check_args(NUMBER_OF_NODES, NUMBER_OF_EDGES, edges, values):
        return {'is_valid': False}

    try:
        edges = [float(s) for s in edges.split()]
        NUMBER_OF_NODES = int(NUMBER_OF_NODES)
        NUMBER_OF_EDGES = int(NUMBER_OF_EDGES)
    except ValueError:
        return {'is_valid': False}

    if len(edges) / 3 != float(NUMBER_OF_EDGES):
        return {'is_valid': False}

    values = values.split(' ')

    vector = []
    for _ in range(NUMBER_OF_NODES):
        try:
            vector.append(float(values.pop(0)))
        except ValueError:
            return {'is_valid': False}

    if not stochastic_validity(vector):
        return {'err': ERR, 'is_valid': False}

    edges = [list(el) for el in zip(*[iter(edges)] * 3)]

    H = np.zeros((NUMBER_OF_NODES, NUMBER_OF_NODES))  # infinitesimal matrix
    for node in range(1, NUMBER_OF_NODES + 1):
        for edge in edges:
            if edge[0] == node:
                H[node - 1][node - 1] -= edge[2]
            if edge[1] == node:
                H[node - 1][int(edge[0] - 1)] += edge[2]

    vector_np = np.array(vector)
    t = Symbol('t')
    p = [Function('p%d' % i) for i in range(1, NUMBER_OF_NODES + 1)]  # list of pi = sympy.Function('pi')
    pt = np.matrix([el(t) for el in p]).transpose()  # pi(t)
    right = (H * pt).tolist()  # right part of ODE-system (matrix)
    eq = [latex(right[i][0]) for i in range(NUMBER_OF_NODES)]  # right part of ODE-system (strings)

    normalization = latex(sum(pt).tolist()[0][0])

    def f(p, t):
        return np.dot(H, p)

    time = np.linspace(0, TIME_MAX, TIME_MAX / TIME_STEP + 1)
    data = odeint(f, vector_np, time).tolist()
    final = data[-1]
    data = [round_list(list(el)) for el in zip(*data[:int(TIME_GRAPH / TIME_STEP + 1)])]  # data for plotting
    time = time[:int(TIME_GRAPH / TIME_STEP + 1)]  # time for plotting

    return {'H': matrix2latex(H.tolist()), 'eq': eq, 'vector': matrix2latex(vector), 'data': data,
            'time': round_list(time.tolist()), 'final': matrix2latex(final), 'edges': edges, 'nn': NUMBER_OF_NODES,
            'normalization': normalization,
            'is_valid': True}

@task_decorate
def stochasticprocesstheoryEx3(request):
    rows = request.GET.get('rows')
    values = request.GET.get('valuesm')
    valuesv = request.GET.get('valuesv')
    fun = request.GET.get('fun')
    if not check_args(rows, values, valuesv) \
            or float(rows) < 1:
        return {'is_valid': False}

    rows = int(rows)

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


    vector = []
    for _ in range(rows):
        try:
            vector.append(float(valuesv.pop(0)))
        except ValueError:
            return {'is_valid': False}


    DU = matrix[0].copy().pop(0)
    DV = matrix[1].copy().pop(1)
    cov = matrix[0].copy().pop(1)
    MU = vector.copy().pop(0)
    MV = vector.copy().pop(1)
    u ,v, t, t1, t2, s = symbols('u v t t1 t2 s')
    dataX = []
    dataY = []
    dataY1 = []
    dataY2 = []
    dataY3 = []
    dataY4 = []
    dataY5 = []
    dataY6 = []
    dataY7 = []
    dataY8 = []
    dataZ1 = []
    dataZ2 = []
    dataZ3 = []
    dataZ4 = []
    dataZ5 = []
    dataZ6 = []
    dataNX1 = []
    dataNY1 = []
    dataNX2 = []
    dataNY2 = []
    dataNX3 = []
    dataNY3 = []
    dataNX4 = []
    dataNY4 = []
    dataNX5 = []
    dataNY5 = []
    dataNX6 = []
    dataNY6 = []
    '''fun = 'u*sint+v*2'''
    fun=parse_expr(fun)
    MX1 = fun.subs({u:MU,v:MV})
    x = fun - MX1
    x1 = x.subs({t:t1})
    x2 = x.subs({t:t2})
    Kx1 = simplify(x1.coeff(u)*x2.coeff(u)*DU+x1.coeff(v)*x2.coeff(u)*cov+x1.coeff(u)*x2.coeff(v)*cov+x1.coeff(v)*x2.coeff(v)*DV)
    D1 = parse_expr(str((simplify(Kx1.subs({t1:t,t2:t})))))

    print(dataX)

    for i in range(-10, 10,1):
     dataX.append(i)
     dataY.append(i)
     dataY1.append(MX1.subs({t : i}))
     dataY5.append(N(D1.subs({t : i})))

    for i in range (-20,20,1):
        for j in range(-20,20,1):
            dataNX1.append(i)
            dataNY1.append(j)
            dataZ1.append(N(Kx1.subs({t1:i,t2:j})))
    Dfun = diff(fun,t)
    MX2 = Dfun.subs({u:MU,v:MV})
    x = Dfun - MX2
    x1 = x.subs({t:t1})
    x2 = x.subs({t:t2})
    Kx2 = simplify(x1.coeff(u)*x2.coeff(u)*DU+x1.coeff(v)*x2.coeff(u)*cov+x1.coeff(u)*x2.coeff(v)*cov+x1.coeff(v)*x2.coeff(v)*DV)
    D2 = simplify(Kx2.subs({t1:t,t2:t}))
    for i in range(-10, 10):
     dataY2.append(N(MX2.subs({t: i})))
     dataY6.append(N(D2.subs({t : i})))

    for i in range (-20,20,1):
        for j in range(-20,20,1):
            dataNX2.append(i)
            dataNY2.append(j)
            dataZ2.append(N(Kx2.subs({t1:i,t2:j})))

    Nfun = fun+Dfun
    MX3 = Nfun.subs({u:MU,v:MV})
    x = Nfun - MX3
    x1 = x.subs({t:t1})
    x2 = x.subs({t:t2})
    Kx3 = simplify(x1.coeff(u)*x2.coeff(u)*DU+x1.coeff(v)*x2.coeff(u)*cov+x1.coeff(u)*x2.coeff(v)*cov+x1.coeff(v)*x2.coeff(v)*DV)
    D3 = simplify(Kx3.subs({t1:t,t2:t}))
    for i in range(-10, 10):
     dataY3.append(N(MX3.subs({t: i})))
     dataY7.append(N(D3.subs({t : i})))

     for i in range(-20, 20, 1):
         for j in range(-20, 20, 1):
             dataNX3.append(i)
             dataNY3.append(j)
             dataZ3.append(N(Kx3.subs({t1: i, t2: j})))

    Ifun = fun.subs(t,s)
    Ifun = integrate(Ifun,(s,0,t))
    MX4 = Ifun.subs({u: MU, v: MV})
    x = Ifun - MX4
    x1 = x.subs({t: t1})
    x2 = x.subs({t: t2})
    Kx4 = simplify(x1.coeff(u)*x2.coeff(u)*DU+x1.coeff(v)*x2.coeff(u)*cov+x1.coeff(u)*x2.coeff(v)*cov+x1.coeff(v)*x2.coeff(v)*DV)
    D4 = simplify(Kx4.subs({t1: t, t2: t}))
    count = 0
    for i in range(-10, 10):
     dataY4.append(N(MX4.subs({t: i})))
     dataY8.append(N(D4.subs({t : i})))

     for i in range(-10, 10, 1):
         for j in range(-20, 20, 1):
             dataNX4.append(i)
             dataNY4.append(j)
             dataZ4.append(N(Kx4.subs({t1: i, t2: j})))

    RXX1 = diff(Kx1,t2)
    RX1X = diff(Kx1,t1)

    for i in range(-10, 10, 1):
        for j in range(-10, 10, 1):
            dataNX5.append(i)
            dataNY5.append(j)
            dataZ5.append(N(RXX1.subs({t1: i, t2: j})))

    for i in range(-20, 20, 1):
        for j in range(-20, 20, 1):
            dataNX6.append(i)
            dataNY6.append(j)
            dataZ6.append(N(RX1X.subs({t1: i, t2: j})))

    return {'f' : fun ,'Df' : Dfun ,'Nf' : Nfun , 'If' : Ifun, 'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector),'DU' : DU,'DV' : DV,'cov' : cov,
             'MX1': MX1,'MX2' : MX2,'MX3' : MX3,'MX4' : MX4,'Kx1' : Kx1,'Kx2' : Kx2,'Kx3' : Kx3,'Kx4' : Kx4,'D1' : D1,
            'D2' : D2,'D3' : D3,'D4' : D4,'RXX1' : RXX1, 'RX1X' : RX1X, 'dataX' : dataX, 'dataY' : dataY, 'dataY1' : dataY1,
             'dataY2' : dataY2,'dataY3' : dataY3,'dataY4' : dataY4,'dataY5' : dataY5,'dataY6' : dataY6,'dataY7' : dataY7,
            'dataY8' : dataY8,'dataZ1' : dataZ1,'dataZ2' : dataZ2,'dataZ3' : dataZ3,'dataZ4' : dataZ4,
            'dataZ5' : dataZ5,'dataZ6' : dataZ6,'dataNX1' : dataNX1,'dataNY1' : dataNY1,'dataNX2' : dataNX2,'dataNY2' : dataNY2,
            'dataNX3' : dataNX3,'dataNY3' : dataNY3,'dataNX4' : dataNX4,'dataNY4' : dataNY4,'dataNX5' : dataNX5,'dataNY5' : dataNY5,
            'dataNX6' : dataNX6,'dataNY6' : dataNY6,'is_valid': True}

'''
@task_decorate
def stochasticprocesstheoryEx4(request):
    k = request.GET.get('k')
    if not k:
        return {'is_valid': False}

    tau = symbols('tau')
    k = parse_expr(k)
    # возвращаем словарь с ответом
    return {'k': k, 'is_valid': True}'''
