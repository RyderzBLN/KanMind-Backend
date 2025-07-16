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


class RegistrationView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            
            saved_account = serializer.save() 
            print(saved_account)
            token, created = Token.objects.get_or_create(user=saved_account)  


            data = {
                'token': token.key,
                'fullname': saved_account.fullname,
                'email': saved_account.email,
                'user_id': saved_account.id

            }
            return Response(data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 👉 Validierungsfehler korrekt handhaben

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Verwenden Sie authenticate() mit dem USERNAME_FIELD (email)
        user = authenticate(
            request, 
            email=email,  # 👉 Direkt 'email' übergeben
            password=password
        )

        if not user:
            return Response(
                {'error': 'Ungültige Login-Daten'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
