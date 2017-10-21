import math
from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from sympy import *
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
                      dict({'template': 'solutions/' + task.section.slug + '/' +
                                        function.__name__ + '.html',
                            'task': task, 'solve': solve},
                           **comments(request, task)))

    return wrapper


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg or not isint(arg):
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
def probabilitytheoryEx1(request):
    def calc_prob(x):
        return round(x / 36, 3)

    N = request.GET.get('N')
    if not check_args(N):
        return {'is_valid': False}

    N = int(N)
    a, b, c = 0, 0, 0
    for i in range(1, 7):
        for j in range(1, 7):
            if i + j <= N:
                a += 1
            if i * j <= N:
                b += 1
            if N != 0 and (i * j) % N == 0:
                c += 1
    solve = {'N': N, 'a': a, 'ans_a': calc_prob(a), 'b': b, 'ans_b': calc_prob(b), 'c': c,
             'ans_c': calc_prob(c), 'is_valid': True}

    return solve


def ex5(K):
    return {'K': K, 'ans': round(1 - 2 / K, 3)}


@task_decorate
def probabilitytheoryEx4(request):
    N = request.GET.get('N')
    K = request.GET.get('K')
    if not check_args(N, K):
        return {'is_valid': False}

    N = int(N)
    K = int(K)

    if N <= 0 or K <= 0 or N >= K:
        return {'is_valid': False}

    P = (K - 1) ** N
    A = math.factorial(K - 1) / math.factorial(K - 1 - N)

    solve = {'K': K, 'N': N, 'P': P, 'A': A, 'ans_a': round(A / P, 3), 'ans_b': round(1 - A / P, 3), 'is_valid': True}

    return solve


@task_decorate
def probabilitytheoryEx8(request):
    k1 = request.GET.get('k1')
    k2 = request.GET.get('k2')
    if not check_args(k1, k2):
        return {'is_valid': False}

    k1 = int(k1)
    k2 = int(k2)

    if k1 < 0 or k2 < 0 or k1 > 100 or k2 > 100:
        return {'is_valid': False}

    P1 = round(k1 / 100, 3)
    P2 = round(k2 / 100, 3)

    P = round(P1 * P2, 3)
    Pa = round(1 - P, 3)
    Pb = round((1 - P1) * (1 - P2), 3)
    Pc = round(P1 * (1 - P2) + P2 * (1 - P1), 3)

    solve = {'k1': k1, 'k2': k2, 'P1': P1, 'P2': P2, 'P': P, 'Pa': Pa, 'Pb': Pb, 'Pc': Pc, 'is_valid': True}

    return solve


def ex7(R, S1, S2):
    ans = (S1 + S2) / (math.pi * R ** 2)
    return {'R': R, 'S1': S1, 'S2': S2, 'ans': round(ans, 3)}


@task_decorate
def probabilitytheoryEx19(request):
    N = request.GET.get('N')
    M = request.GET.get('M')
    P = request.GET.get('P')

    if not check_args(N, M):
        return {'is_valid': False}
    if not P:
        return {'is_valid': False}

    P = re.sub(',', '.', str(P))
    N = int(N)
    M = int(M)
    try:
        P = float(P)
    except ValueError:
        return {'is_valid': False}

    if N <= 0 or M <= 0 or M >= N or P < 0 or P > 1:
        return {'is_valid': False}

    lam = N * P
    lam_m = lam ** M
    e_lam = math.exp(-lam).real
    m_fact = math.factorial(M)
    Pa = round(lam_m * e_lam / m_fact, 6)
    solve = {'Pa': Pa, 'N': N, 'M': M, 'P': P, 'lam': lam, 'is_valid': True}
    return solve
