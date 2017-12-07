import math
from bisect import bisect, bisect_left
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
    NUMBER_OF_VALUES = len(numbers_sort)
    # data for the third graph (EFR)
    unique_numbers = set(numbers_sort)
    unique_numbers = list(unique_numbers)
    unique_numbers.sort()

    max = unique_numbers[len(unique_numbers)-1]
    min = unique_numbers[0]

    count = 0
    efr = [0.0, 0.0]
    for unique_number in unique_numbers:
        count += numbers_sort.count(unique_number) / NUMBER_OF_VALUES
        efr.append(round(count, 2))
    efr.append(1.0)

    index_efr = [min - 0.5]
    index_efr.extend(unique_numbers)
    index_efr.append(max + 0.5)
    index_efr.append(max + 1.0)

    # data for the fourth graph (gistogramma)
    NUMBER_OF_INTERVALS = 10
    step = (max - min) / NUMBER_OF_INTERVALS
    grid_gist = [round(min + i*step, 2) for i in range(NUMBER_OF_INTERVALS + 1)]

    gist = []
    gist_value = bisect(numbers_sort, grid_gist[1])
    gist.append(round(gist_value / NUMBER_OF_VALUES / step, 2))
    gist_sum = gist_value

    for i in range(2, len(grid_gist)):
        gist_value = (bisect(numbers_sort, grid_gist[i]) - gist_sum)
        gist.append(round(gist_value / NUMBER_OF_VALUES / step, 2))
        gist_sum += gist_value

    index_polygon = [round((grid_gist[i]+grid_gist[i+1])/2, 2) for i in range(len(grid_gist)-1)]



    myvalue = {'make': 1, 'top': 2}

    return {'numbers': numbers, 'index': index, 'numbers_sort': numbers_sort, 'efr': efr, 'index_efr': index_efr,
            'gist': gist, 'index_polygon': index_polygon, 'grid_gist': grid_gist,
            'is_valid': True, 'myjson': json.JSONDecoder(myvalue)}
