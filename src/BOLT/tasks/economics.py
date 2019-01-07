import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import re


def check_args(*args):
    """Проверка на float"""
    for arg in args:
        if not arg:
            return False
        try:
            float(arg)
        except ValueError:
            return False
    return True


def in_per(num):
    """Перевод в проценты"""
    return round(num * 100, 1)


def rnd(number):
    return round(number, 3)


@task_decorate
def economicsEx1(request):
    osn_k = request.GET.get('osn-k')
    d = request.GET.get('d')
    r = request.GET.get('r')
    f_pl = request.GET.get('f-pl')
    ob_k = request.GET.get('ob-k')
    ch = request.GET.get('ch')
    k_o = request.GET.get('k-o')

    if not check_args(osn_k, d, r, f_pl, ob_k, ch, k_o):
        return {'is_valid': False}

    osn_k = float(osn_k)
    d = float(d)
    r = float(r)
    f_pl = float(f_pl)
    ob_k = float(ob_k)
    ch = int(ch)
    k_o = float(k_o)

    profit = d - r
    assets = osn_k + ob_k
    r_act = profit / assets
    sk = assets - k_o
    r_sk = profit / sk
    r_pr = profit / d
    kpl = ob_k / k_o
    ook = d / osn_k
    r_osk = profit / osn_k
    srm = osn_k / ch
    r_obk = profit / ob_k
    k_ob = d / ob_k
    t_ob = f_pl / k_ob
    v = d / ch

    solve = {'osn_k': osn_k, 'd': d, 'r': r, 'f_pl': f_pl, 'ob_k': ob_k, 'ch': ch, 'k_o': k_o, 'profit': rnd(profit),
             'assets': rnd(assets), 'sk': rnd(sk), 'kpl': rnd(kpl), 'ook': rnd(ook), 'srm': rnd(srm), 'k_ob': rnd(k_ob),
             't_ob': rnd(t_ob), 'v': rnd(v), 'r_act': rnd(r_act), 'r_sk': rnd(r_sk), 'r_pr': rnd(r_pr),
             'r_osk': rnd(r_osk), 'r_obk': rnd(r_obk), 'r_act_per': in_per(r_act), 'r_sk_per': in_per(r_sk),
             'r_pr_per': in_per(r_pr), 'r_osk_per': in_per(r_osk), 'r_obk_per': in_per(r_obk), 'is_valid': True}
    return solve
