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
import json

@task_decorate
def mathstatisticsEx1(request):
    numbers_input = request.GET.get('numbers')

    if not numbers_input:
        return {'is_valid': False}
    try:
        numbers = [float(v) for v in filter(None, re.split("[, ]+", numbers_input))]
    except ValueError:
        return {'is_valid': False}

    # data for the first graph
    index = [i for i in range(1, len(numbers) + 1)]
    # data for the second graph
    numbers_sort = numbers.copy()
    numbers_sort.sort()
    # data for the third graph
    unique_numbers = set(numbers_sort)
    unique_numbers = list(unique_numbers)
    unique_numbers.sort()

    count = 0
    efr = [0.0]
    for el in unique_numbers:
        count += numbers_sort.count(el)/len(numbers_sort)
        efr.append(count)
    efr.append(1.0)

    a = unique_numbers[0]-1.0
    b = unique_numbers[len(unique_numbers)-1]+1.0
    index_efr = [a]
    index_efr.extend(unique_numbers)
    index_efr.append(b)

    myvalue = {'make': 1, 'top': 2}

    return {'numbers': numbers, 'index': index, 'numbers_sort': numbers_sort, 'efr': efr, 'index_efr': index_efr,
            'is_valid': True, 'myjson': json.JSONDecoder(myvalue)}
