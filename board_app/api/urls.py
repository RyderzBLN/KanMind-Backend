from django.urls import path
from .views import BoardViews

urlpatterns = [
    path('', BoardViews.as_view(), name='board-list'),
]