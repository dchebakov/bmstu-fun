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


@task_decorate
def mathstatisticsEx1(request):
    numbers = request.GET.get('numbers')
    if not numbers:
        return {'is_valid': False}

    return {'numbers': numbers, 'is_valid': True}
