from django.urls import path
from .views import todoHomePage, todoDetails, createToDo, deleteToDo, finishToDo, finishedToDos


urlpatterns = [
    path('', todoHomePage, name='todo_index'),
    path('<int:id>', todoDetails, name='todo_details'),
    path('create/', createToDo, name='new_todo_form'),
    path('delete/', deleteToDo, name='delete_todo'),
    path('finish/', finishToDo, name='finish_todo'),
    path('finished/', finishedToDos, name='finished_todo_list'),
]
#
