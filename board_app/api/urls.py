from django.urls import path
<<<<<<< HEAD
from .views import BoardViews, BoardDetailView, BoardMembersUpdateView, BoardUpdateView

urlpatterns = [
    path('', BoardViews.as_view(), name='board-list'),
    path('<int:pk>/', BoardUpdateView.as_view(), name='board-update'),
]
=======
from .views import BoardViews

urlpatterns = [
    path('', BoardViews.as_view(), name='board-list'),
]
>>>>>>> parent of 57cd40b (add GET /api/boards/{board_id}/)
