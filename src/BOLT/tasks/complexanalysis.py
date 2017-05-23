import math
from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re
from .probabilitytheory import task_decorate, comments, check_args, isint


@task_decorate
def complexanalysisEx1(request):
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