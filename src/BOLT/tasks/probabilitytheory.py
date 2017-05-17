import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm


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
                      dict({'temapltename': 'solutions/probabilitytheory/' +
                                            function.__name__ + '.html',
                            'task': task, 'solve': solve},
                           **comments(request, task)))

    return wrapper


@task_decorate
def probabilitytheoryEx1(request):
    def calc_prob(x):
        return round(x / 36, 3)

    N = request.GET.get('N')
    if not N:
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

    return {'N': N, 'a': a, 'ans_a': calc_prob(a), 'b': b, 'ans_b': calc_prob(b), 'c': c,
            'ans_c': calc_prob(c), 'is_valid': True}


def ex5(K):
    return {'K': K, 'ans': round(1 - 2 / K, 3)}


def ex4(K, N):
    P = (K - 1) ** N
    A = math.factorial(K - 1) / math.factorial(K - 1 - N)
    return {'K': K, 'N': N, 'P': P, 'A': A, 'ans_a': round(A / P, 3), 'ans_b': round(1 - A / P, 3)}


def ex7(R, S1, S2):
    ans = (S1 + S2) / (math.pi * R ** 2)
    return {'R': R, 'S1': S1, 'S2': S2, 'ans': round(ans, 3)}
