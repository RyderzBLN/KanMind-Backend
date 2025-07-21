from django.urls import path

from .views import BoardViews, BoardDetailView, BoardMembersUpdateView, BoardUpdateView

urlpatterns = [
    path('', BoardViews.as_view(), name='board-list'),
    path('<int:pk>/', BoardUpdateView.as_view(), name='board-update'),
]

