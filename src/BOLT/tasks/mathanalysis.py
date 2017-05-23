import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments, check_args, isint
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re



