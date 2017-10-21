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
    numbers = request.GET.get('numbers')
    if not numbers:
        return {'is_valid': False}

    myvalue = {'make': 1, 'top': 2}

    return {'numbers': numbers, 'is_valid': True, 'myjson': json.JSONDecoder(myvalue)}
