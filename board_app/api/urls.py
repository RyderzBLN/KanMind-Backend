from django.urls import path
from .views import BoardViews, BoardDetailView, AssignedTicketsView, RewieverView, TaskCreateView, CommentDeleteView, TaskDetailView, TaskCommentsView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedTicketsView.as_view(), name='assigned-tickets'),
    path('boards/', BoardViews.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskCreateView.as_view(), name='reviewing-tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='reviewing-tasks'),
    path('tasks/reviewing/', RewieverView.as_view(), name='reviewing-tasks'),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', 
         CommentDeleteView.as_view(), 
         name='task-comment-detail'),
    

]