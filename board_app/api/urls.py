from django.urls import path
from .views import BoardViews, BoardDetailView

urlpatterns = [
    path('', BoardViews.as_view(), name='board-list'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]