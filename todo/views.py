from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import ModelForm, Textarea
from todo.models import ToDo
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import datetime


class ToDoModelForm(ModelForm):
    class Meta:
        model = ToDo
        fields = ['title', 'desc', 'private']
        labels = {
            'title': 'Feladat rövid megnevezése',
            'desc': 'Feladat részletes leírása',
            'private': 'Saját feladat?'
        }
        widgets = {
            'desc': Textarea(attrs={'cols': 40, 'rows': 5}),
        }


def render_not_supported_methode():
    not_supported_method_response = HttpResponse()
    not_supported_method_response.status_code = 405
    not_supported_method_response.content('Nem megfelelő HTTP method')
    return not_supported_method_response


@login_required
def createToDo(request):
    if request.method == 'POST':
        form = ToDoModelForm(request.POST)

        if form.is_valid():
            created_todo = form.save(commit=False)
            created_todo.author = request.user
            created_todo.save()

            return HttpResponseRedirect(reverse('todo_details', args=[str(created_todo.id)]))
        else:
            return render(request, 'create_todo.html', {'form': form})

    elif request.method == 'GET':
        form = ToDoModelForm()
        return render(request, 'create_todo.html', {'form': form})
    else:
        return render_not_supported_methode()


@login_required
def todoDetails(request, id, error=None):
    theOne = get_object_or_404(ToDo, pk=id)

    if request.user != theOne.author and theOne.private:
        return HttpResponseRedirect(reverse('login') + f'?next={request.path}')

    context = {'todo': theOne}

    if error:
        context['error'] = error

    return render(request, 'todo_details.html', context)


@login_required
def todoHomePage(request):
    todos = ToDo.objects\
        .filter(finished_at=None)\
        .filter(Q(author=request.user) | Q(private=False))\
        .all()
    already_done = ToDo.objects\
        .exclude(finished_at=None)\
        .filter(Q(author=request.user) | Q(private=False))\
        .all()[:2]

    return render(request, 'todo_list.html', {'todos': todos, 'already_done': already_done})


@login_required
def finishedToDos(req):
    limit = 4
    page = 0

    if req.GET:
        page = int(req.GET.get('page', 0))

    offset = page * limit

    already_done = ToDo.objects\
        .exclude(finished_at=None) \
        .filter(Q(author=req.user) | Q(private=False)) \
        .all()[offset: offset + limit]
    done_count = ToDo.objects\
        .exclude(finished_at=None) \
        .filter(Q(author=req.user) | Q(private=False)) \
        .count()

    last_page = done_count // limit
    next_page = page + 1 if page != last_page else None
    prev_page = page - 1 if page > 0 else None

    return render(
        req,
        'finished_list.html',
        {
            'todos': already_done,
            'offset': offset,
            'limit': limit,
            'all_item_num': done_count,
            'last_page': last_page,
            'next_page': next_page,
            'prev_page': prev_page,
        }
    )


def finishToDo(request):
    if request.method == 'POST':
        error = None
        todo_id = None

        try:
            todo_id = request.POST.get('id')
            if todo_id:
                todo_id = int(todo_id)
                todo = ToDo.objects.get(id=todo_id)

                if todo.finished_at:
                    todo.finished_at = None
                else:
                    todo.finished_at = datetime.datetime.now()

                todo.save()
            else:
                error = 'Nem megfelelő azonosító lett átadva.'
        except:
            error = 'Ismeretlen hiba miatt, a feladat megoldása meghiúsult.'

        if error:
            return todoDetails(request, todo_id, error)
        else:
            return HttpResponseRedirect(reverse('todo_index'))
    else:
        return render_not_supported_methode()


def deleteToDo(request):
    if request.method == 'POST':
        error = None
        todo_id = None

        try:
            todo_id = request.POST.get('id')
            if todo_id:
                todo_id = int(todo_id)
                ToDo.objects.get(id=todo_id).delete()
            else:
                error = 'Nem megfelelő azonosító lett átadva.'
        except:
            error = 'Ismeretlen hiba miatt, a törlés meghiúsult.'

        if error:
            return todoDetails(request, todo_id, error)
        else:
            return HttpResponseRedirect(reverse('todo_index'))
    else:
        return render_not_supported_methode()
