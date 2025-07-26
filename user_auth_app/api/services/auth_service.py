from rest_framework.authtoken.models import Token
from user_auth_app.api.serializers import RegistrationSerializer, LoginSerializer
from django.contrib.auth import authenticate


def register_user(data):
    serializer = RegistrationSerializer(data=data)

    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }, None

    return None, serializer.errors


def login_user(email, password, request=None):
    user = authenticate(request=request, email=email, password=password)

    if not user:
        return None, {'error': 'Ungültige Login-Daten'}

    token, _ = Token.objects.get_or_create(user=user)

    data = {
        'token': token.key,
        'fullname': user.fullname,
        'email': user.email,
        'user_id': user.id
    }
    return data, None