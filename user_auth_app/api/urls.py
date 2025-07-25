from django.urls import path
from .views import RegistrationView, CustomLoginView, EmailCheckView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check')
]