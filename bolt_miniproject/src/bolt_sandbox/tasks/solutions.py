from django.shortcuts import render
from ..models import Task, Section
from .. import views

def task_decorate(function):
    def wrapper(request):
        task = Task.objects.get(function_name=function.__name__)
        solve = function(request)
        return render(request, 'task.html', 
                    {'temapltename': 'solutions/' + function.__name__ + '.html', 'task': task, 'solve': solve, 'sections': Section.objects.all()})

    return wrapper

def check_args(*args): # Общая проверка
    for arg in args:
        if not arg:
            return False
    return True    

@task_decorate
def solution(request):
    
    a = request.GET.get('a')
    b = request.GET.get('b')
    
    if not check_args(a, b):
        return {'is_valid': False}

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return {'is_valid': False}
    
    S = a * b
    S = round(S, 3)
    
    solve = {'a': a, 'b': b, 'S': S, 'is_valid': True}
    
    return solve