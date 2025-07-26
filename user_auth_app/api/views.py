from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import RegistrationSerializer
from .serializers import LoginSerializer
from django.contrib.auth import get_user_model

from .services.auth_service import (
    register_user,
    login_user
)

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data, errors = register_user(request.data)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_201_CREATED)
    

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        data, error = login_user(email=email, password=password, request=request)

        if error:
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        return Response(data, status=status.HTTP_200_OK)
    

class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
