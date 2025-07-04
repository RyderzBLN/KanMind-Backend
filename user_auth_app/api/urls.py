from django.urls import path
from .views import RegistrationView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', obtain_auth_token, name='api_token_auth')  # 🔗 POST /api/registration/
]