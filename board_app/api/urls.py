from django.urls import path
from .views import BoardViews, BoardDetailView, AssignedTicketsView, RewieverView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedTicketsView.as_view(), name='assigned-tickets'),
    path('boards/', BoardViews.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/reviewing/', RewieverView.as_view(), name='reviewing-tasks'),
]