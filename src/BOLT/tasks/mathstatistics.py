import math
from bisect import bisect, bisect_left
from scipy.stats import chi2, norm
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
    nadezhnost = request.GET.get('1-alpha')

    if not numbers_input or not nadezhnost:
        return {'is_valid': False}
    nadezhnost = re.sub(',', '.', str(nadezhnost))
    try:
        numbers = [float(v) for v in filter(None, re.split("[, ]+", numbers_input))]
        nadezhnost = float(nadezhnost)
    except ValueError:
        return {'is_valid': False}

    alpha = 1 - nadezhnost

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
    NUMBER_OF_UNIQUE_VALUES = len(unique_numbers)
    counts = [numbers_sort.count(unique_number) for unique_number in unique_numbers]

    max = unique_numbers[NUMBER_OF_UNIQUE_VALUES-1]
    min = unique_numbers[0]

    efr_value = 0
    efr = [0.0, 0.0]
    for count in counts:
        efr_value += count / NUMBER_OF_VALUES
        efr.append(round(efr_value, 2))
    efr.append(1.0)

    index_efr = [min - 0.5]
    index_efr.extend(unique_numbers)
    index_efr.append(max + 0.5)
    index_efr.append(max + 1.0)

    # data for the fourth graph (gistogramma)
    if NUMBER_OF_UNIQUE_VALUES > 10:
        NUMBER_OF_INTERVALS = 10
    else:
        NUMBER_OF_INTERVALS = NUMBER_OF_UNIQUE_VALUES

    step = (max - min) / NUMBER_OF_INTERVALS
    if step == 0:
        step = 1
    grid_gist = [round(min + i*step, 2) for i in range(NUMBER_OF_INTERVALS + 1)]

    gist = []
    gist_value = bisect(numbers_sort, grid_gist[1])
    gist.append(round(gist_value / NUMBER_OF_VALUES / step, 2))
    gist_sum = gist_value

    gist_values = [gist_value]
    for i in range(2, len(grid_gist)):
        gist_value = (bisect(numbers_sort, grid_gist[i]) - gist_sum)
        gist.append(round(gist_value / NUMBER_OF_VALUES / step, 2))
        gist_values.append(gist_value)
        gist_sum += gist_value

    index_polygon = [round((grid_gist[i]+grid_gist[i+1])/2, 2) for i in range(len(grid_gist)-1)]

    # Ravnomernoe raspredelenie
    L_RAVN = 2
    ravn_a = ( NUMBER_OF_VALUES * min - max ) /(NUMBER_OF_VALUES-1)
    ravn_b = ( NUMBER_OF_VALUES * max - min ) /(NUMBER_OF_VALUES-1)
    ravn_levo_a = min - (max - min)*(1-alpha**(1/NUMBER_OF_VALUES))
    ravn_pravo_b = max + (max - min)*(1-alpha**(1/NUMBER_OF_VALUES))

    ravn_p = [(grid_gist[i + 1] - grid_gist[i]) / (ravn_b - ravn_a) for i in range(NUMBER_OF_INTERVALS)]

    ravn_w = 0
    for i in range(NUMBER_OF_INTERVALS):
        ravn_w += (gist_values[i])**2/NUMBER_OF_VALUES/ravn_p[i]
    ravn_w -= NUMBER_OF_VALUES
    ravn_wkr = chi2.ppf(nadezhnost, NUMBER_OF_INTERVALS-1-L_RAVN)
    if ravn_w < ravn_wkr:
        ravn_answer = "Статистика Пирсона меньше критического значения, гипотеза принимается с надежностью " + str(
            nadezhnost) + "."
    else:
        ravn_answer = "Статистика Пирсона больше критического значения, гипотеза отклоняется с надежностью " + str(
            nadezhnost) + "."

    # Pokazatelnoe raspredelenie
    L_POKAZ = 1
    pokaz_x = 0
    for i in range(NUMBER_OF_INTERVALS):
        pokaz_x += gist_values[i] * index_polygon[i]
    pokaz_x = pokaz_x / NUMBER_OF_VALUES
    pokaz_lambda = 1 / pokaz_x

    pokaz_levo_lambda = float(pokaz_lambda * (1 - norm.ppf(1 - alpha / 2) / sqrt(NUMBER_OF_VALUES)))
    pokaz_pravo_lambda = float(pokaz_lambda * (1 + norm.ppf(1 - alpha / 2) / sqrt(NUMBER_OF_VALUES)))
    print(pokaz_pravo_lambda)

    pokaz_p = [math.exp(-pokaz_lambda * grid_gist[i]) - math.exp(-pokaz_lambda * grid_gist[i + 1]) for i in
               range(NUMBER_OF_INTERVALS)]

    pokaz_w = 0
    for i in range(NUMBER_OF_INTERVALS):
        pokaz_w += (gist_values[i]) ** 2 / NUMBER_OF_VALUES / pokaz_p[i]
    pokaz_w -= NUMBER_OF_VALUES
    pokaz_wkr = chi2.ppf(nadezhnost, NUMBER_OF_INTERVALS - 1 - L_POKAZ)
    if pokaz_w < pokaz_wkr:
        pokaz_answer = "Статистика Пирсона меньше критического значения, гипотеза принимается с надежностью " + str(
            nadezhnost) + "."
    else:
        pokaz_answer = "Статистика Пирсона больше критического значения, гипотеза отклоняется с надежностью " + str(
            nadezhnost) + "."


    myvalue = {'make': 1, 'top': 2}

    return {'numbers': numbers, 'index': index, 'numbers_sort': numbers_sort, 'efr': efr, 'index_efr': index_efr,
            'gist': gist, 'index_polygon': index_polygon, 'grid_gist': grid_gist, 'unique_numbers': unique_numbers,
            'counts': counts, 'gist_values': gist_values, 'step': round(step, 2), 'number_of_values': NUMBER_OF_VALUES,
            'number_of_intervals': NUMBER_OF_INTERVALS, 'min': min, 'max': max, 'nadezhnost': nadezhnost,
            'l_ravn': L_RAVN, 'l_pokaz': L_POKAZ,

            'ravn_a': round(ravn_a, 2), 'ravn_b': round(ravn_b, 2), 'ravn_levo_a': round(ravn_levo_a, 2), 'ravn_pravo_b': round(ravn_pravo_b, 2),
            'ravn_p': ravn_p, 'ravn_w': round(ravn_w, 2), 'ravn_wkr': round(ravn_wkr, 2), 'ravn_answer': ravn_answer,

            'pokaz_x': round(pokaz_x, 2), 'pokaz_lambda': round(pokaz_lambda, 2), 'pokaz_p': pokaz_p,
            'pokaz_w': round(pokaz_w), 'pokaz_wkr': round(pokaz_wkr, 2),
            'pokaz_answer': pokaz_answer, 'pokaz_levo_lambda': round(pokaz_levo_lambda, 2),
            'pokaz_pravo_lambda': round(pokaz_pravo_lambda, 2),

            'is_valid': True, 'myjson': json.JSONDecoder(myvalue)}
